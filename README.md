# fixr1
Bulk update web pages of a live site using Python and ftplib.

Tailored for a site that has only two levels of directories, a base
directory and a large number of subdirectories one level down. So only 
traverses two levels of directories.

Set ftp login credentials and defaults in config.py
Then from the command line run

    python fixr1.py
and follow the prompts.
