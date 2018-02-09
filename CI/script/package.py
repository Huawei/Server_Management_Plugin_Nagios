#coding=utf-8
import tarfile
import os
import glob
import shutil

def excludeSvn(tarinfo):
    return False

def copyFile(filesouce, filetarget):
    '''
    '移动文件
    '''
    if os.path.isfile(filesouce):
        shutil.copy2(filesouce , os.path.join(filetarget))
    elif os.path.isdir(filesouce):
        dirname = os.path.basename(filesouce)
        if not os.path.isdir(os.path.join(filetarget) + os.path.sep + dirname):
            os.mkdir(os.path.join(filetarget) + os.path.sep + dirname)
        for infile in glob.glob(os.path.join(filesouce, "*")):
            copyFile(infile, os.path.join(filetarget) + os.path.sep + dirname)

def removeFile(filepath):
        filepath = os.path.join(filepath)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            if len(os.listdir(filepath)) != 0:
                for infile in glob.glob(os.path.join(filepath, "*")):
                    removeFile(infile)
            os.rmdir(filepath)

def reset(tarinfo):
    if -1 == str(tarinfo.name).lower().find('/.svn'):
        return tarinfo

def main():
    nagiosName='Huawei eSight Server Management Plug-in (for Nagios)'
    
    nagiosdir=os.getcwd() + os.path.sep + nagiosName

    srcdir_bin='/usr1/jenkins/workspace/nagios-plugin-package' + os.path.sep + 'SRC'+os.path.sep + 'bin'
    srcdir_etc='/usr1/jenkins/workspace/nagios-plugin-package' + os.path.sep + 'SRC'+os.path.sep + 'etc'
    srcdir_libexec='/usr1/jenkins/workspace/nagios-plugin-package' + os.path.sep + 'SRC' + os.path.sep + 'libexec'
    srcdir_setup='/usr1/jenkins/workspace/nagios-plugin-package' + os.path.sep + 'SRC' + os.path.sep+  'setup.py'

    if not os.path.isdir(nagiosdir) :
        os.mkdir(nagiosdir)

    copyFile(srcdir_bin,nagiosdir)
    copyFile(srcdir_etc,nagiosdir)
    copyFile(srcdir_libexec,nagiosdir)
    copyFile(srcdir_setup,nagiosdir)

    tar=tarfile.open(nagiosName+'.gz','w:gz')
    tar.add(nagiosName,exclude=excludeSvn,filter=reset)
    tar.close()

    removeFile(nagiosdir)

main()

