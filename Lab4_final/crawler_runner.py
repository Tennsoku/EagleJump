import os

DB_file_path_delete = "./backend/frontend/db*.*"
DB_file_path= "./backend/frontend/db/"
crawler_path = "./backend/run_backend_test.py"

def crawler_runner():
	
   	os.system("rm -f %s" %DB_file_path_delete)
	os.system("python %s" %crawler_path) #running the crawler
	print "Crawler Finished"


	os.system("mv ./lexicon.db %s" %DB_file_path) #move datebase files to frontend
	os.system("mv ./inverted_index.db %s" %DB_file_path)
	os.system("mv ./document_index.db %s" %DB_file_path)
	os.system("mv ./page_rank.db %s" %DB_file_path)
	os.system("mv ./document_title.db %s" %DB_file_path)

	print "DB setup Finished"


crawler_runner()

