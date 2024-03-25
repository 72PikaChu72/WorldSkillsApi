import sqlite3

def StartDatabase():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS Users (
                        email TEXT NOT NULL PRIMARY KEY,
                        password TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL
                    )
                ''')
        conn.execute('''CREATE TABLE IF NOT EXISTS Files (
                        fileid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        owner_email TEXT NOT NULL,
                        accesses TEXT,
                        FOREIGN KEY (owner_email) REFERENCES Users (email)
                    )
                ''')
def isUserExists(email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE email = ?)",(email,))
        return bool(cursor.fetchone()[0])
def getUserSharedFiles(email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT fileid, filename FROM Files WHERE accesses LIKE ?",('%'+email+'%',))
        return cursor.fetchall()
def getFileAccesses(fileid):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT accesses FROM Files WHERE fileid = ?",(fileid,))
        return cursor.fetchone()

def getUserInfoByEmail(email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM Users WHERE email = ?",(email,))
        return cursor.fetchone()
def DeleteFileAccesses(fileid, email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT accesses FROM Files WHERE fileid = ?",(fileid,))
        accessesout = cursor.fetchone()
        if accessesout[0]:
            accesses = accessesout[0].split(':')
            if email in accesses:
                accesses.remove(email)
                accesses = ':'.join(accesses)
                conn.execute("UPDATE Files SET accesses = ? WHERE fileid = ?",(accesses,fileid,))
            else:
                return 10000

def getUserFiles(email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT fileid, filename FROM Files WHERE owner_email = ?",(email,))
        return cursor.fetchall()

def AppendFileAccesses(fileid, email):
    with sqlite3.connect('database.db') as conn:
        if not isUserExists(email):
            return 5000
        
        
        cursor = conn.execute("SELECT accesses FROM Files WHERE fileid = ?",(fileid,))
        accessesout = cursor.fetchone()
        if accessesout[0]:
            if email in accessesout[0].split(':'):
                return 10000
            accesses = accessesout[0] + ':' + email
        else:
            accesses = email
        conn.execute("UPDATE Files SET accesses = ? WHERE fileid = ?",(accesses,fileid,))
def IsUserFileOwner(fileid,email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT owner_email FROM Files WHERE fileid = ? and owner_email = ?",(fileid, email,))
        try:
            return cursor.fetchone()[0]
        except:
            return False

def IsUserAllowedToFile(fileid,email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT owner_email FROM Files WHERE fileid = ? and (owner_email = ? or accesses LIKE ?)",(fileid, email,'%'+email+'%',))
        try:
            return cursor.fetchone()[0]
        except:
            return False

def loginUser(email, password):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password,))
        return cursor.fetchone()

def registerfile(filename:str, owneremail:str):
    with sqlite3.connect('database.db') as conn:
        conn.execute("INSERT INTO Files (filename, owner_email) VALUES (?, ?)", (filename,owneremail,))
    return getFileId(filename, owneremail)
def deletefile(fileid):
    with sqlite3.connect('database.db') as conn:
        conn.execute("DELETE FROM Files WHERE fileid = ?", (fileid,))
def getFilenameWithFileId(fileid):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT filename FROM Files WHERE fileid = ?", (fileid,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return None

def renameFile(fileId, newName):
    with sqlite3.connect('database.db') as conn:
        conn.execute("UPDATE Files SET filename = ? WHERE fileid = ?", (newName, fileId,))

def getFileId(filename:str, owneremail:str):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT fileid FROM Files WHERE filename = ? AND owner_email = ?", (filename, owneremail,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return None

def createUser(email, password, first_name, last_name):
    with sqlite3.connect('database.db') as conn:
        if isUserExists(email):
            return False
        else:
            conn.execute("INSERT INTO Users (email, password, first_name, last_name) VALUES (?,?,?,?)", (email, password, first_name, last_name,))
            return True
StartDatabase()
