import PyPDF2
import os
import argparse
import re

def get_pdf_outline_info(outline, reader, parent_title=""):
    """
    递归地从PDF大纲中提取所有书签的标题和页码。
    PyPDF2的页码是基于0的索引。
    """
    outline_info = []
    for item in outline:
        if isinstance(item, PyPDF2.generic.Destination):
            try:
                title = item.title
                # PyPDF2.generic.Destination.page 是一个 IndirectObject，需要解析
                # 获取页码索引，然后通过 reader.get_page_number(page_object) 获取实际页码
                page_index = reader.get_page_number(item.page)
                outline_info.append({"title": title, "page_index": page_index})
            except Exception as e:
                # 某些书签可能已损坏或指向无效目标，跳过它们
                print(f"警告：跳过一个无效的书签 '{getattr(item, 'title', '未知标题')}'。")
                continue
        elif isinstance(item, list):
            # 处理嵌套书签
            outline_info.extend(get_pdf_outline_info(item, reader, parent_title))
    return outline_info

def calculate_page_ranges(outline_info, total_pages):
    """
    根据书签信息和总页数计算每个书签对应的页码范围。
    返回的页码是基于1的索引。
    """
    sections = []
    
    # 按页码排序书签，确保顺序正确
    outline_info.sort(key=lambda x: x["page_index"])

    for i, item in enumerate(outline_info):
        title = item["title"]
        start_index = item["page_index"]

        end_index = total_pages - 1 # 默认结束页为文档最后一页（0-based）
        if i + 1 < len(outline_info):
            end_index = outline_info[i+1]["page_index"] - 1 # 下一个书签的起始页码前一页

        # 确保结束页码不小于起始页码
        if start_index <= end_index:
            sections.append({
                "name": title,
                "start_page": start_index + 1, # 转换为1-based
                "end_page": end_index + 1    # 转换为1-based
            })
        elif i == len(outline_info) - 1: # 如果是最后一个书签，且start_index > end_index (可能因为只有一个书签或书签指向最后一页)
            sections.append({
                "name": title,
                "start_page": start_index + 1,
                "end_page": total_pages
            })

    return sections

def perform_pdf_split(reader, sections, output_dir, add_sequence=True):
    """
    根据计算出的页码范围将PDF拆分为多个文件。
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"正在将拆分后的PDF文件保存到：{output_dir}")

    total_sections = len(sections)
    num_digits = len(str(total_sections))

    for i, section in enumerate(sections):
        writer = PyPDF2.PdfWriter()
        start_page_index = section['start_page'] - 1 # 转换为0-based
        end_page_index = section['end_page'] - 1     # 转换为0-based

        # 确保页码范围有效
        if start_page_index < 0 or end_page_index >= len(reader.pages) or start_page_index > end_page_index:
            print(f"警告：跳过无效页码范围的部分 '{section['name']}' ({section['start_page']}-{section['end_page']})")
            continue

        for page_num in range(start_page_index, end_page_index + 1):
            writer.add_page(reader.pages[page_num])

        # 清理文件名，移除非法字符
        cleaned_name = re.sub(r'[\\/:*?"<>|]', '', section['name'])
        
        if add_sequence:
            sequence_prefix = f"{i+1:0{num_digits}d}_"
            output_filename = f"{sequence_prefix}{cleaned_name}.pdf"
        else:
            output_filename = f"{cleaned_name}.pdf"
            
        output_filepath = os.path.join(output_dir, output_filename)

        with open(output_filepath, 'wb') as output_pdf:
            writer.write(output_pdf)
        print(f"已创建文件: {output_filename}, 原始页码: {section['start_page']}-{section['end_page']}")

def split_pdf_by_chapters(pdf_path, output_dir=None, add_sequence=True): # 默认值改为 None
    """
    根据PDF书签自动拆分PDF文件。
    """
    if not os.path.exists(pdf_path):
        print(f"错误：输入文件 '{pdf_path}' 不存在。")
        return

    # 获取原始PDF文件名（不含扩展名）
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]

    if output_dir is None:
        # 如果未指定输出目录，则在原始PDF文件同目录中创建子文件夹
        pdf_directory = os.path.dirname(pdf_path)
        final_output_dir = os.path.join(pdf_directory, pdf_basename)
    else:
        # 如果指定了输出目录，则在该目录中创建子文件夹
        final_output_dir = os.path.join(output_dir, pdf_basename)

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            print(f"PDF文件总页数：{total_pages}")

            outline = reader.outline
            if not outline:
                print("PDF文件中没有找到书签（大纲）信息。无法进行基于书签的拆分。")
                return

            outline_info = get_pdf_outline_info(outline, reader)
            
            # 过滤掉页码为None的书签（可能指向外部链接等）
            outline_info = [item for item in outline_info if item["page_index"] is not None]

            if not outline_info:
                print("未找到有效的书签信息。无法进行基于书签的拆分。")
                return

            sections = calculate_page_ranges(outline_info, total_pages)
            
            if not sections:
                print("未识别到任何可拆分的部分。")
                return

            perform_pdf_split(reader, sections, final_output_dir, add_sequence) # 使用新的输出目录
            print("\nPDF拆分完成！")

    except Exception as e:
        print(f"处理PDF文件时发生错误：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="根据PDF书签自动拆分PDF文件。")
    parser.add_argument("input_pdf", help="要拆分的PDF文件路径。")
    parser.add_argument("-o", "--output_dir", default=None, # 默认值改为 None
                        help="拆分后PDF文件的输出目录 (默认为原始PDF文件同目录下的子文件夹)。")
    parser.add_argument("--no-sequence", action="store_true",
                        help="不为拆分后的文件添加序列号前缀。")
    
    args = parser.parse_args()
    
    split_pdf_by_chapters(args.input_pdf, args.output_dir, add_sequence=not args.no_sequence)