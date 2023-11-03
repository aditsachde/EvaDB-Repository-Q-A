import evadb
import subprocess
import tempfile
import os
import shutil
import mimetypes
import nbformat
import csv

# Connect to EvaDB
cursor = evadb.connect().cursor()

# Replace this with a working open api key, or,
# remove the line and set the env var
os.environ['OPENAI_KEY'] = 'sk-replace-me'

# Function which is used to load a repository into EvaDB
def load_repository(cursor, repo_url):
  temp_dir = tempfile.mkdtemp()
  target_directory = "repo"
  git_clone_command = ["git", "clone", repo_url, target_directory]
  subprocess.check_call(git_clone_command, cwd=temp_dir)
  repo_path = os.path.join(temp_dir, target_directory)

  id = 1
  rows = [['id', 'name', 'text']]

  for root, dirs, files in os.walk(repo_path):
      dirs[:] = [d for d in dirs if not d.startswith('.')]
      files = [f for f in files if not f.startswith('.')]

      for file in files:
        if not any(d.startswith('.') for d in root.split(os.path.sep)):
          file_path = os.path.join(root, file)
          mime_type, _ = mimetypes.guess_type(file_path)
          rel_path = os.path.relpath(os.path.join(root, file), repo_path)
          is_text_file = mime_type and mime_type.startswith('text/')
          if is_text_file:
            with open(file_path, 'r', encoding='utf-8') as file:
              file_content = file.read()
            rows.append([id, rel_path, file_content])
            id += 1

          elif file_path.endswith('.ipynb'):
            with open(file_path, 'r', encoding='utf-8') as file:
              notebook_content = nbformat.read(file, as_version=4)

            file_content = ''
            for cell in notebook_content['cells']:
              if cell.cell_type == 'markdown' or cell.cell_type == 'code':
                file_content += cell.source
                file_content += "\n\n"
            rows.append([id, rel_path, file_content])
            id += 1

  csv_file = os.path.join(temp_dir, "output.csv")

  with open(csv_file, mode="w", newline="") as file:
      writer = csv.writer(file)
      for row in rows:
          writer.writerow(row)

  cursor.query('''
  DROP TABLE IF EXISTS repository
  ''').df()

  cursor.query('''
  CREATE TABLE repository
  (id INTEGER,
  name TEXT(150),
  text TEXT(150000))
  ''').df()

  cursor.query(f'''
  LOAD CSV '{csv_file}' INTO repository
  ''').df()

  shutil.rmtree(temp_dir)

# Load the reference repository
load_repository(cursor, "https://github.com/microsoft/AI-For-Beginners.git")

# Ask the same question on a bunch of different files
response = cursor.query('''
  SELECT ChatGPT('What is this lesson about?', text)
  FROM repository LIMIT 10
''').df()

print(response)

# Ask a single question, referencing a single lesson
response2 = cursor.query('''
  SELECT ChatGPT('What is this lesson about?', text)
  FROM repository WHERE name = 'lessons/5-NLP/16-RNN/RNNPyTorch.ipynb'
''').df()

print(response2["chatgpt.response"][0])