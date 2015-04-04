# Edit published static web pages via ftp
import ftplib, os, socket

# Specify HOST, USERNAME, PASSWORD, BASEDIR, KEYWORD in your config.py file
from config import *

def ftp_connect():
	try:
		con = ftplib.FTP(HOST)
	except (socket.error, socket.gaierror), e:
		print 'ERROR: cannot reach "%s"' % HOST
		return
	print '*** Connected to host "%s"' % HOST
	return con

def ftp_login(con):
	try:
	    con.login(USERNAME, PASSWORD)
	except ftplib.error_perm:
	    print 'ERROR: cannot login'
	    con.quit()
	    return
	print '*** Logged in as ', USERNAME

def ftp_cwd(con, target_dir=BASEDIR):
	try:
	    con.cwd(target_dir)
	except ftplib.error_perm:
	    print 'ERROR: cannot CD to "%s"' % target_dir
	    con.quit()
	    return
	print '*** Changed to "%s" folder' % target_dir

def ftp_getdir(con):
	# Gets the directory listing
	ls = []
	try:
		con.dir(ls.append)
	except ftplib.error_perm:
		print 'ERROR: cannot get directory listing for "%s"' % con.pwd()
		return
	print '*** Got directory listing in returned variable'
	return ls

def get_directories(ls):
	# Gets just the directories from the directory listing
	dirs = [item.split(' ')[-1] for item in ls if 'd' in item.split(' ')[0]]
	dirs = dirs[2:] # Strip out the . and .. directories
	print '*** Got the list of directories'
	return dirs
	
def get_phpfiles(con, ls):
	# Gets just the php files from the directory listing
	file_names = [item.split(' ')[-1] for item in ls]
	php_files = [item for item in file_names if '.php' in item and '.bak' not in item]
	print '*** Got the list of php files'
	
	for f in php_files:
		try:
			con.retrbinary('RETR %s' % f, open(f, 'wb').write)
		except ftplib.error_perm:
			print 'ERROR: cannot read file "%s"' % f
			os.unlink(f)
		else:
			print '*** Downloaded "%s"' % f
			
	print '*** Done retrieving the php files'
	return php_files
	
def fix_phpfiles(php_files):
	# Deletes the line containing KEYWORD
	for infile in php_files:
		with open(infile, 'r') as ifile:
			with open('temp.php', 'wb') as outfile:
			    for line in ifile:
			        if KEYWORD not in line:
						outfile.write(line)
			outfile.close()
		ifile.close()
		print '*** Fixed file "%s"' % infile
		os.rename(infile, infile + '.bak')
		os.rename('temp.php', infile)
	print '*** Finished fixing all files in this directory'

def upload_fixedfiles(con, php_files):
	# Uploads the fixed files and backups of the original files
	pfiles = []
	for item in php_files:
		pfiles.append(item)
		pfiles.append(item + '.bak') # Add backup files to the list
	for f in pfiles:
		try:
			con.storbinary('STOR %s' % f, open(f, 'rb'))
		except ftplib.error_perm:
			print 'ERROR: cannot upload file "%s"' % f
			os.unlink(f)
		else:
			print '*** Uploaded "%s"' % f
			os.remove(f)
	print '*** Done uploading the php files'	

def delete_line():
	con, dirs = ftp_setup()
	#con = ftp_connect()
	#ftp_login(con)
	#ftp_cwd(con, BASEDIR) # Start in BASEDIR
	#ls = ftp_getdir(con) # Get the directory listing
	#dirs = get_directories(ls) # Extract just the dirs to traverse
	for d in dirs:
		ftp_cwd(con, d) # Change into working directory
		ls = ftp_getdir(con)
		php_files = get_phpfiles(con, ls)
		fix_phpfiles(php_files)
		upload_fixedfiles(con, php_files)
		ftp_cwd(con, BASEDIR) # Back up to BASEDIR
	con.quit()
	print '*** All done. Disconnected from "%s"' % HOST
	
def delete_file(fname):
	con, dirs = ftp_setup()
	#con = ftp_connect()
	#ftp_login(con)
	#ftp_cwd(con, BASEDIR) # Start in BASEDIR
	#ls = ftp_getdir(con) # Get the directory listing
	#dirs = get_directories(ls) # Extract just the dirs to traverse
	for d in dirs:
		ftp_cwd(con, d) # Change into working directory
		ls = ftp_getdir(con)
		fn = [item.split(' ')[-1] for item in ls]
		if fname in fn:
			con.delete(fname)
			print '*** Deleted ' + fname + ' from directory ' + d
		else:
			print '*** ' + fname + ' not found in directory ' + d
		ftp_cwd(con, BASEDIR)
	con.quit()
	print '*** Deleted file ' + fname + ' from all subdirectories'
	
def find_badword(BADWORD, ls):
	# Makes a list of files that contain BADWORD
	pass

def list_subdirectories():
	con, dirs = ftp_setup()
	print 'Subdirectories of %s' % BASEDIR
	print dirs
	
def ftp_setup():
	con = ftp_connect()
	ftp_login(con)
	ftp_cwd(con, BASEDIR) # Start in BASEDIR
	ls = ftp_getdir(con) # Get the directory listing
	dirs = get_directories(ls) # Extract just the dirs to traverse
	return con, dirs

############
### Main ###
############
print 'Make changes to a live website via ftp'
print 'Set your ftp login credentials in the config.py file'
print 'Starts in BASEDIR - set BASEDIR default in the config.py file'
print 'Makes changes to first level of subdirectories below BASEDIR'
print 'BASEDIR is currently set to %s\n' % BASEDIR

choice = ''
while choice != 99:
	print 'Choices:'
	print '1 - change BASEDIR'
	print '2 - delete a file from subdirs of BASEDIR'
	print '3 - delete line containing KEYWORD in all files in subdirs of BASEDIR'
	print '4 - make list of files in subdirs of BASEDIR containing BADWORD'
	print '5 - list subdirectories of BASEDIR'
	print '99 - exit\n'
	choice = int(raw_input('Choose an option from above: '))
	if choice == 1: # Change BASEDIR
		print 'BASEDIR is currently %s' % BASEDIR
		BASEDIR = raw_input('Set new BASEDIR: ')
		print 'BASEDIR now set to %s\n' % BASEDIR
	elif choice == 2: # Delete file
		print 'Selected: delete a file from all subdirectories of %s' % BASEDIR
		FILENAME = raw_input('Enter FILENAME to delete: ')
		confirm = raw_input('Delete "%s" in subdirs of %s. y or n?: ' % (FILENAME, BASEDIR))
		if confirm == 'y':
			delete_file(FILENAME)
		else:
			print 'Action canceled\n'
	elif choice == 3: # Delete line containing KEYWORD
		print 'Selected: delete line containing KEYWORD from all files in subdirectories of %s' % BASEDIR
		KEYWORD = raw_input('Enter KEYWORD: ')
		print 'KEYWORD is now "%s"\n' % KEYWORD
	elif choice == 4: # Find BADWORD
		print 'Chose 3'
		print 'BADWORD is currently set to "%s"\n' % BADWORD
	elif choice == 5: # List subdirectories
		list_subdirectories()
		print ''
	elif choice == 99:
		print 'Exiting now'
		break
	else:
		print 'Invalid choice. Try again.\n'
