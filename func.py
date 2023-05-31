import os
import shutil
import subprocess
from os.path import join


def file_associate(path):
    """
    path是一个文件夹，
    该文件夹下包含若干个子文件夹，每个子文件夹中有同样个数的文件（strict=True 模式下必须一致，否则报错）
    依次取出每个文件夹中的文件，构成一个元组，
    这些文件构成的多个元组，以list的形式存储，并返回。list[tuple,tuple,...]
    --dir:path
    ----sub_dir_a
    ------sub_dir_a_files
    ----sub_dir_b
    ------sub_dir_b_files
    ----sub_dir_c
    ------sub_dir_c_files
    ...
    return [(sub_dir_a_file,sub_dir_b_file,sub_dir_c_file,...),...]
    """
    sub_dirs = [join(path, _) for _ in os.listdir(path)]
    content = []
    for user_dir in sub_dirs:
        filepaths = [join(user_dir, _) for _ in os.listdir(user_dir)]
        content.append(filepaths)
    maps = list(zip(*content, strict=True))
    return maps


def create_dir(path, force=False):
    """
    :param path:
    :param force: if force is true,when dir has exists, dir will be removed,then recreate dir.
    :return:
    """
    create_ok = False
    if os.path.exists(path) and force:
        shutil.rmtree(path)
    else:
        try:
            os.mkdir(path)
            create_ok = True
        except Exception as e:
            # ignore this error.
            ...
    if not create_ok:
        os.makedirs(path)
    if not os.path.exists(path):
        raise f"create dir {path} failed."


def create_dirs(paths, force=False):
    for path in paths:
        create_dir(path, force=force)


def delete_dir(path):
    shutil.rmtree(path)


def delete_dirs(path):
    for p in path:
        delete_dir(p)


def file_helper(path):
    """
    输入文件夹路径：
    返回两个list：所有文件，所有文件夹
    :param path:
    :return:
    """
    paths = [join(path, _) for _ in os.listdir(path)]
    files = []
    dirs = []
    for p in paths:
        if os.path.isdir(p):
            dirs.append(p)
        if os.path.isfile(p):
            files.append(p)
    return dirs, files


def get_files(path, suffix=None):
    """
    suffix 可以指定或获取某个类型的文件，如 suffix = ".bmp", suffix = ".mp4", 将返回带该后缀的文件名
    :param path:
    :param suffix:
    :return:
    """
    _, origin_files = file_helper(path)
    if suffix:
        files = [file for file in origin_files if file.endswith(suffix)]
    else:
        files = origin_files
    return files


def get_dirs(path):
    dirs, _ = file_helper(path)
    return dirs


def execute_command(cmd: str):
    execute_ok = 0
    completed = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = completed.returncode
    stdout = completed.stdout
    stderr = completed.stderr
    if ret == execute_ok:
        if stdout:
            print(f"Command {cmd} execute result is:{stdout}")
    else:
        print(f"ErrorCommand:{cmd}\nErrorInfo:{stderr}\n")
