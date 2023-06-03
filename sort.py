import sys
import shutil
import os
from string import ascii_letters, digits


CATEGORIES = {'archives': ('zip', 'gz', 'tar'),
            'audio': ('mp3', 'ogg', 'wav', 'amr', 'flac'),
            'documents': ('doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx', 'odt'),
            'images': ('jpeg', 'png', 'jpg', 'svg', 'webp'),
            'video': ('avi', 'mp4', 'mov', 'mkv')
            }


def create_categories():

    for folder_name in CATEGORIES:
        if folder_name in os.listdir(BASE_FOLDER):
            continue
        folder_path = os.path.join(BASE_FOLDER, folder_name)
        
        os.makedirs(folder_path)
        

def normalize(file_name):

    TRANSLITERATION = {'ї': 'yi', 'ё': 'yo', 'є': 'ye', 'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh',
                    'з': 'z', 'и': 'y', 'і': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 
                    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 
                    'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', 'Ё': 'Yo','Є': 'Ye', 'Ї': 'Yi', 'А': 'A', 'Б': 'B', 
                    'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'І': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 
                    'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 
                    'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
                    }  

    correct_characters = ascii_letters + digits + '_'       
    file_name, extension = os.path.splitext(file_name)
    file_name = ''.join([char if char in correct_characters else TRANSLITERATION[char] 
                         if char in TRANSLITERATION else '_'
                         for char in file_name])   

    return file_name + extension


def check_name_conflict(folder_path, name):   
    
    files = os.listdir(folder_path)
    
    if name not in files:
        return name
        
    filename, extension = os.path.splitext(name)
    counter = 1
    new_filename = f"{filename}_{counter}{extension}"
    
    while new_filename in files:
        counter += 1
        new_filename = f"{filename}_{counter}{extension}"
    
    return new_filename
    

def rename_file(destination_folder, full_file_path): 

    file_name = os.path.basename(full_file_path)
    file_path = os.path.dirname(full_file_path) 

    new_file_name = normalize(file_name)
    if new_file_name != file_name:
        new_file_name = check_name_conflict(file_path, new_file_name)
    new_file_name = check_name_conflict(destination_folder, new_file_name)

    new_full_file_path = os.path.join(file_path, new_file_name)
      
    os.rename(full_file_path, new_full_file_path)

    return new_full_file_path


def move_file(file_path, destination_folder):
    new_full_file_path = rename_file(destination_folder, file_path)
    shutil.move(new_full_file_path, destination_folder)


def get_category_path(file_name):
    extension = os.path.splitext(file_name)[1].lower()[1:]
    if extension:
    
        for category, extensions in CATEGORIES.items():
            if extension in extensions:
                category_path = os.path.join(BASE_FOLDER, category)

                return category_path

    return None


def move_files():
    for root, dirs, files in os.walk(BASE_FOLDER):
        if os.path.basename(root) in CATEGORIES:
            continue
        for file in files:
            category_path = get_category_path(file)
            if category_path:            
                move_file(os.path.join(root, file), category_path)
            else:
                rename_file(root, os.path.join(root, file))
            

def unpack_archives():
    
    folder_path = os.path.join(BASE_FOLDER, 'archives')
    files = os.listdir(folder_path)

    for file in files:
        file_path = os.path.join(folder_path, file)

        if os.path.splitext(file)[1][1:] in CATEGORIES['archives']:
            
            shutil.unpack_archive(file_path, folder_path)          
            os.remove(file_path)       


def delete_empty_folders():

    for root, dirs, files in os.walk(BASE_FOLDER, topdown=False):        

        for directory in dirs:
            path = os.path.join(root, directory)
            
            if os.path.basename(path) in CATEGORIES:
                        continue

            if not os.listdir(path): 
                os.rmdir(path)


def rename_all_folders():
    for root, dirs, files in os.walk(BASE_FOLDER):
        for directory in dirs:

            if directory in CATEGORIES:
                continue

            new_folder_name = normalize(directory)

            if new_folder_name != directory:
               new_folder_name = check_name_conflict(root, new_folder_name)

            full_new_folder_name = os.path.join(root, new_folder_name) 
            full_old_folder_name = os.path.join(root, directory)          
            os.rename(full_old_folder_name, full_new_folder_name)


def disassemble_junk():
    create_categories()
    move_files()
    unpack_archives()
    delete_empty_folders()
    rename_all_folders()


if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print("Не вказано ім'я папки для сортування.")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]):
        print(f"Шлях {sys.argv[1]} не веде до папки.")
        sys.exit(1)

    BASE_FOLDER = sys.argv[1]
    
    disassemble_junk()    

    print("Сортування папки", BASE_FOLDER, "завершено.")