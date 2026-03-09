import os
import shutil
import pydub
import xml.etree.ElementTree as ET
from pydub import AudioSegment

def process_playlist():
    # Запрашиваем пути у пользователя
    spl_input = input("Enter filename or path to .spl file: ").strip().strip('"')
    target_dir = input("Enter your target directory path: ").strip().strip('"')
    
    # Новый запрос: конвертировать или нет
    convert_choice = input("Do you want to convert non-MP3 files to MP3? (y/n): ").strip().lower()
    do_convert = convert_choice == 'y'
    
    # Вызываем основную функцию обработки, передаем флаг конвертации
    run_processing(spl_input, target_dir, do_convert)

def run_processing(spl_path, target_dir, do_convert):
    # Preparing folder
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"[*] Created folder: {target_dir}")
        
    try:
        # Parsing input SPL
        tree = ET.parse(spl_path)
        root = tree.getroot()
        
        success_count = 0
        sounds = root.findall('Sound')
        total_count = len(sounds) 
        
        # Исправлено: путь к папке с SPL
        spl_dir = os.path.dirname(os.path.abspath(spl_path))
        
        print(f"[*] Starting to process files...")
        
        # 2. Loop over the sounds
        for index, sound in enumerate(sounds, 1):
            old_path = sound.get('url', '').strip()
            
            if not os.path.isabs(old_path):
                old_path = os.path.join(spl_dir, old_path)
                
            if not old_path or not os.path.exists(old_path):
                print(f"[!] #{index}/{total_count} File not found, skipping {old_path}")
                continue
            
            base_name = os.path.basename(old_path)
            name, ext = os.path.splitext(base_name)
            
            # Определяем, будем ли реально конвертировать
            # Конвертируем ТОЛЬКО если пользователь нажал 'y' И файл не mp3
            should_convert = do_convert and ext.lower() not in ['.mp3']
            
            target_ext = '.mp3' if should_convert else ext.lower()
            new_file_name = f"{name}{target_ext}"
            
            counter = 1
            while os.path.exists(os.path.join(target_dir, new_file_name)):
                new_file_name = f"{name}_{counter}{target_ext}"
                counter += 1
                
            dest_path = os.path.abspath(os.path.join(target_dir, new_file_name))
            
            try:
                if should_convert:
                    print(f"[*] #{index}/{total_count} Converting {base_name} to MP3...") # Пишем converting...
                    audio = AudioSegment.from_file(old_path)
                    audio.export(dest_path, format="mp3")
                    status = "CONVERTED"
                else:
                    shutil.copy2(old_path, dest_path)
                    status = "OK"
                    
                sound.set('url', dest_path)
                success_count += 1
                print(f"[{status}] #{index}/{total_count}: {base_name} -> {new_file_name}")
                
            except Exception as e:
                print(f"[ERR] #{index}/{total_count} Failed to process {base_name}: {e}")
                    
        # 3. Saving the patched .spl
        new_spl_name = os.path.basename(spl_path)
        new_spl_path = os.path.join(target_dir, new_spl_name)
        
        tree.write(new_spl_path, encoding='utf-8', xml_declaration=True)
        
        print("-" * 30)
        print(f"[DONE] Transfered Files: {success_count}/{total_count}")
        print(f"[INFO] New playlist saved here: {new_spl_path}")

    except Exception as e:
        print(f"Error when working with script: {e}")

if __name__ == "__main__":
    process_playlist()