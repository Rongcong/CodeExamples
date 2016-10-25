import hashlib;
import os;

image_path = os.path.join("static", "images_backup");
sql_file = open(os.path.join("sql", "load_image.sql"), 'w');
dic = {'sports':1, 'football':2, 'world':3, 'space':4}
for rt, dirs, files in os.walk(image_path):
    for f in files:
        prefix = (f.split('_'))[0]
        albumid = dic.get(prefix)
        m = hashlib.md5(str(albumid) + f)
        fmt = (f.split('.'))[1];
        print prefix, f, fmt
        # rename all the images names to the hash type name
        os.rename(os.path.join(image_path, f), os.path.join(image_path, m.hexdigest() + '.' + fmt))
        sql_file.write('INSERT INTO Photo (picid, format) VALUES (\'');
        sql_file.write(m.hexdigest() + '\', \'' + fmt + '\')\n');
        sql_file.write('INSERT INTO Contain (albumid, picid) VALUES (');
        sql_file.write(str(albumid) + ', \'' + m.hexdigest() + '\')\n\n');
sql_file.close();

