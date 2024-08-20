import os
import codecs

def read_file_with_fallback(file_path, preferred_encoding='utf-8'):
    encodings = [preferred_encoding, 'iso-8859-1', 'windows-1252']
    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as file:
                return [line.strip() for line in file if line.strip()]
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Unable to decode the file {file_path} with the attempted encodings: {encodings}")

def read_category_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            category_name = os.path.splitext(filename)[0].replace('.', '-')
            file_path = os.path.join(directory, filename)
            try:
                lines = read_file_with_fallback(file_path)
                hosts = []
                for line in lines:
                    if '=' in line:
                        display_name, actual_host = line.split('=', 1)
                        hosts.append((display_name.strip(), actual_host.strip()))
                    else:
                        hosts.append((line.strip(), line.strip()))
                data.append({
                    'name': category_name,
                    'title': f"{category_name}",
                    'hosts': hosts
                })
            except UnicodeDecodeError as e:
                print(f"Warning: Couldn't read {filename}. Error: {str(e)}")
    return data

def generate_menu_section():
    menu_section = []
    menu_section.append("+ v6Test")
    menu_section.append("menu = IPv6延遲檢測")
    menu_section.append("title = IPv6")
    menu_section.append("probe = FPing6")
    menu_section.append("remark = <h2>此監測項目為IPv6的連線情況，將監測該ASN到各節點品質的情況</h2>")
    return menu_section

def generate_slaves_section(slaves_list):
    return [f"slaves = {' '.join(slaves_list)}", ""]

def generate_category_section(item):
    category_section = []
    category_section.append(f"++ {item['name']}")
    category_section.append(f"title = {item['title']}")
    category_section.append(f"menu = {item['title']}")
    host_list = [f"/v6Test/{item['name']}/{display_name.replace('.', '-')}" for display_name, _ in item['hosts']]
    category_section.append(f"host = {' '.join(host_list)}")
    return category_section

def generate_host_section(display_name, actual_host):
    host_section = []
    # Generate the title with the format: "{display_name} - {actual_host}"
    title = f"{display_name} - {actual_host}" if display_name != actual_host else display_name
    host_section.append(f"+++ {display_name.replace('.', '-')}")
    host_section.append(f"menu = {display_name}")
    host_section.append(f"title = {title}")
    host_section.append(f"host = {actual_host}")
    host_section.append("")
    return host_section

def generate_config(data, slaves_list):
    config = []

    # Generate the initial menu, title, and remark sections
    config.extend(generate_menu_section())

    # Add the slave configuration
    config.extend(generate_slaves_section(slaves_list))

    # Generate the configuration for each category
    for item in data:
        config.extend(generate_category_section(item))

        # Generate configuration for each host in the category
        for display_name, actual_host in item['hosts']:
            config.extend(generate_host_section(display_name, actual_host))

    return "\n".join(config)

if __name__ == "__main__":
    try:
        category_dir = './category'
        #slaves_list = ['CHv6', 'anotherone', 'apple', 'banana']
        slaves_list = []
        data = read_category_files(category_dir)
        config = generate_config(data, slaves_list)
        print(config)
        
        with codecs.open('generated_config.txt', 'w', encoding='utf-8') as file:
            file.write(config)
        print("Configuration has been written to 'generated_config.txt'")
    except FileNotFoundError:
        print("Error: category directory or files not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
