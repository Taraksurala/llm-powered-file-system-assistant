from pathlib import Path
from zipfile import BadZipFile
from pypdf import PdfReader
from docx import Document

SUPPORTED_EXTENSIONS = (".pdf", ".txt", ".docx")

# Function to read a file and check if it exists and if the format is supported
def read_file(filepath: str) -> dict:
    
    # convert string to path
    path = Path(filepath)

    # Check if file exists and is a file
    if path.exists() and path.is_file():
        # Get File Extension
        file_extension = path.suffix.lower()

        # Get metadata of the file
        metadata = {
            "name": path.name,
            "filepath": str(path),
            "file_type": file_extension,
            "size": path.stat().st_size,
            "created": path.stat().st_ctime ,
            "modified": path.stat().st_mtime
        }

        # Check if File Extension is supported or not
        if file_extension in SUPPORTED_EXTENSIONS:
            content = ''
            if file_extension == ".txt":
                try:
                    with open(path, 'r') as file:
                        content = file.read()
                except Exception as e:
                    return { "success": False , "message" :f"Error reading TXT file: {str(e)}", "metadata": metadata }
            elif file_extension == ".pdf":
                try:
                    reader = PdfReader(path)
                    pdf_text = []
                    number_of_pages = len(reader.pages)
                    metadata["page_count"] = number_of_pages
                    for page_num in range(number_of_pages):
                        text = reader.pages[page_num].extract_text()
                        if text is None:
                            pass
                        elif not text.strip():
                            pass
                        else:
                            pdf_text.append(text)

                    content = "\n".join(pdf_text)
                except Exception as e:
                    return { "success": False , "message" :f"Error reading PDF file: {str(e)}", "metadata": metadata }
            
            elif file_extension == ".docx":
                try:
                    document = Document(path)
                    docx_text = []
                    for paragraph in document.paragraphs:
                        if not paragraph.text.strip():
                            pass
                        else:
                            docx_text.append(paragraph.text)
                    content = "\n".join(docx_text)
                except BadZipFile:
                    return { "success": False , "message" :"Error reading DOCX file: The file is not a valid DOCX file or it is corrupted", "metadata": metadata }
                except Exception as e:
                    return { "success": False , "message" :f"Error reading DOCX file: {str(e)}", "metadata": metadata }
            if not content.strip():
                return { "success": False , "message" :"File is empty", "content": content, "metadata": metadata }
            else:
                return { "success": True , "message" :"File exists and the format is supported", "content": content, "metadata": metadata }
        else:
            return { "success": False , "message" :"File format is not supported" }
    else: 
        return { "success": False, "message": "File does not exist" }


# Function to list all files in a directory and check if they exist and if the format is supported

def list_files(filepath: str, extension: str = None) -> dict:
    # convert string to path
    path = Path(filepath)

    # print(f"Path input for the list files function {path}" )
    # set flag for enabling filter as per the extension
    filter_enable = False

    if extension is None:
        filter_enable = False
    else: 
        filter_enable = True
        # extension = extension.lower()
        extension = "." + extension.lstrip(".").lower()

    # Initialize the files list
    files_list = []

    # Check if the path exists or not and if it is a directory or not
    if path.exists() and path.is_dir():
        # Iterate the childs inside the directory
        for child in path.iterdir():
            file_extension = child.suffix.lower()
            # print(f"file_extension {file_extension}")
            # Check if the child is file or not 
            # child_path = Path(child) 
            # print(Path(child).name) 
            if child.is_file():
                metadata = {
                    "name": child.name,
                    "filepath": str(child),
                    "file_type": file_extension,
                    "size": child.stat().st_size,
                    "modified": child.stat().st_mtime
                }
                
                if filter_enable:
                    if file_extension == extension:
                        files_list.append(metadata)     
                    else:
                        pass
                else:
                    files_list.append(metadata)
            else:
                pass
        if not files_list:
            return {"success": True, "files_list": files_list, "message": 'No matching files found' }
        else:
            return {"success": True, "files_list": files_list  }
    else:
     return {"success":False, "message": "Directory is invalid or does not exists" } 


def write_file(filepath: str, content: str) -> dict:

    # convert the string to path
    path = Path(filepath)

    path.parent.mkdir(parents=True, exist_ok=True)

    try:    
        with open(path, 'w') as file:
            file.write(content)
        return {"success": True, "message": f"File written successfully at {str(path)}"}
    except Exception as e:
        return {"success": False, "message": f"Error writing file at {str(e)}"}

def search_in_file(filepath: str, keyword: str) -> dict:
    # search_string validation

    if not keyword.strip():
        return {"message":"Search keyword cannot be empty","success": False}
    else:

        # read file content
        result = read_file(filepath)

        if result["success"]:
            content = result["content"]

            content_lower = content.lower()
            keyword_lower = keyword.lower()

            match_list = []
            start_index = 0
            while True:
                index = content_lower.find(keyword_lower, start_index)
                if index == -1:
                    break
                # print(f"Found '{search_string}' at index: {index}")
                match_data = {
                    "position" : index,
                    "keyword": keyword,
                    "context": content[max(0, index-30):min(len(content), index+len(keyword)+30)]
                }
                match_list.append(match_data)
                start_index = index + len(keyword_lower)

            if not match_list:
                return {"success": True, "keyword": keyword, "metadata": result["metadata"], "message":"No matches found", "matches":match_list, "match_count": 0}
            else:
                return {"success": True, "keyword": keyword,  "metadata": result["metadata"], "matches":match_list, "match_count": len(match_list)}
        else:
            return result
    


if __name__ == "__main__":
    # print(read_file("sample.txt"))
    # print(read_file("resumes/"))
    # print(read_file("sampledoc.docx"))

    # print(list_files("resumes/",'.jpg'))

    # print(list_files("resumes/"))
    # print(list_files("resumes/", ".pdf"))
    # print(list_files("resumes/", "PDF"))
    # print(list_files("resumes/", ".jpg"))
    # print(list_files("does_not_exist/"))
    # write_file(
    #     "output/sample.txt",
    #     "Hello from my file system assistant!"
    # )

    print(search_in_file("resumes/resume_tarak_full_stack_5_years_plus.pdf", "express"))