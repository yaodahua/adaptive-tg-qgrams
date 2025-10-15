import csv
import numpy as np
import math
import os
import re
from scipy.stats import ranksums


def get_p_statistics(p_file_csv, print_stats=False):
    pp = []
    with open(p_file_csv, "r") as f:
        reader = csv.reader(f)
        _ = next(reader)
        for r in reader:
            # 添加错误处理：检查行是否有足够的列
            if len(r) >= 2:
                try:
                    pp.append(float(r[1]))
                except (ValueError, IndexError):
                    # 跳过格式错误的行
                    continue
            else:
                # 跳过列数不足的行
                continue
    
    # 如果没有有效数据，返回默认值
    if len(pp) == 0:
        return 0, 0.0, 0.0, 0.0
    
    stderr = np.std(pp) / math.sqrt(len(pp))
    relstderr = 1 if np.mean(pp) == 0 else stderr / np.mean(pp)
    if print_stats:
        print(f"{len(pp)} {np.mean(pp):.2e} {stderr:.2e} {100 * relstderr:.2f}%")
    return len(pp), np.mean(pp), stderr, relstderr


def get_f_t_statistics(f_t_file_csv, print_stats=False):
    ff = []
    tt = []
    try:
        with open(f_t_file_csv, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            # 清理列名中的空格
            header = [col.strip() for col in header]
            
            for r in reader:
                # 跳过空行
                if not r:
                    continue
                # 清理每行数据中的空格
                r = [cell.strip() for cell in r]
                # 检查是否有足够的列
                if len(r) >= 3:
                    try:
                        ff.append(float(r[1]))
                        tt.append(float(r[2]))
                    except (ValueError, IndexError) as e:
                        print(f"警告：跳过格式错误的数据行: {r}, 错误: {e}")
                        continue
                else:
                    print(f"警告：跳过列数不足的数据行: {r}")
                    continue
        
        # 检查是否有有效数据
        if len(ff) == 0:
            raise ValueError(f"文件 {f_t_file_csv} 中没有有效数据")
            
        stderr_ff = np.std(ff) / math.sqrt(len(ff))
        relstderr_ff = 1 if np.mean(ff) == 0 else stderr_ff / np.mean(ff)
        stderr_tt = np.std(tt) / math.sqrt(len(tt))
        relstderr_tt = 1 if np.mean(tt) == 0 else stderr_tt / np.mean(tt)
        if print_stats:
            print(f"{len(ff)} {np.mean(ff)} {stderr_ff} {100 * relstderr_ff:.2f}%")
            print(f"{len(tt)} {np.mean(tt):.2e} {stderr_tt:.2e} {100 * relstderr_tt:.2f}%")
        return (
            len(ff),
            np.mean(ff),
            stderr_ff,
            relstderr_ff,
            len(tt),
            np.mean(tt),
            stderr_tt,
            relstderr_tt,
        )
    except Exception as e:
        raise ValueError(f"处理文件 {f_t_file_csv} 时出错: {e}")


def get_statistics(p_file_csv, f_t_file_csv):
    pp = []
    ff = []
    tt = []
    with open(p_file_csv, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            pp.append(float(r[1]))
    with open(f_t_file_csv, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            ff.append(float(r[1]))
            tt.append(float(r[2]))
    return (np.mean(ff), np.mean(tt), np.mean(pp))
    # print(f'{np.mean(ff):.1f} {np.mean(tt):.3f} {np.mean(pp):.2e}')


def print_all_statistics(dir, lens):
    for size in lens:
        rand = get_statistics(
            f"{dir}/P_measure_rand_{size}.csv", f"{dir}/F_T_measure_rand_{size}.csv"
        )
        dist = get_statistics(
            f"{dir}/P_measure_dist_{size}.csv", f"{dir}/F_T_measure_dist_{size}.csv"
        )
        bigrams = get_statistics(
            f"{dir}/P_measure_bigrams_{size}.csv",
            f"{dir}/F_T_measure_bigrams_{size}.csv",
        )
        tfidf = get_statistics(
            f"{dir}/P_measure_tfidf_{size}.csv",
            f"{dir}/F_T_measure_tfidf_{size}.csv",
        )
        print(f"{size}\t\t\tRand\t\tDist\t\tBigrams\t\tTF-IDF")
        print(f"F-meas\t\t{rand[0]:.1f}\t\t{dist[0]:.1f}\t\t{bigrams[0]:.1f}\t\t{tfidf[0]:.1f}")
        print(f"T-meas\t\t{rand[1]:.3f}\t\t{dist[1]:.3f}\t\t{bigrams[1]:.3f}\t\t{tfidf[1]:.3f}")
        print(f"P-meas\t\t{rand[2]:.2e}\t{dist[2]:.2e}\t{bigrams[2]:.2e}\t{tfidf[2]:.2e}")
        print()


def write_summary_statistics(delay=False, is_triangle=False):
    triangle_dir = ""
    lengths = [100, 1000, 10000, 66225]
    if is_triangle:
        triangle_dir = "_tr"
        lengths = [10, 100, 300]
    del_dir = ""
    if delay:
        del_dir = "_del"
    
    # 检查哪些生成方法有数据文件
    available_methods = []
    for gen in ["rand", "dist", "bigrams", "tfidf", "simidf"]:
        # 检查是否有任意长度的P-measure文件存在
        for ll in lengths:
            p_filename = f"results{triangle_dir}{del_dir}/P_measure_{gen}_{ll}.csv"
            if os.path.isfile(p_filename):
                available_methods.append(gen)
                break
    
    # 如果没有找到任何方法的数据，则跳过写入
    if not available_methods:
        print("警告：未找到任何方法的统计数据文件，跳过summary_stats.csv的生成")
        return
    
    with open(f"results{triangle_dir}{del_dir}/summary_stats.csv", "w") as f:
        f.write(
            "Str len, Gen, P-Runs, P-Mean, P-Err, F-Runs, F-Mean, F-Err, T-Runs, T-Mean, T-Err\n"
        )
        for ll in lengths:
            for gen in available_methods:
                filename = f"results{triangle_dir}{del_dir}/P_measure_{gen}_{ll}.csv"
                p_runs, p_mean, p_stderr, p_relstderr = "", "", "", ""
                if os.path.isfile(filename):
                    try:
                        p_runs, p_mean, p_stderr, p_relstderr = get_p_statistics(filename)
                    except (IndexError, ValueError, FileNotFoundError) as e:
                        print(f"警告：处理文件 {filename} 时出错: {e}")
                        continue
                
                filename = f"results{triangle_dir}{del_dir}/F_T_measure_{gen}_{ll}.csv"
                (
                    f_runs,
                    f_mean,
                    f_stderr,
                    f_relstderr,
                    t_runs,
                    t_mean,
                    t_stderr,
                    t_relstderr,
                ) = ("", "", "", "", "", "", "", "")
                if os.path.isfile(filename):
                    try:
                        (
                            f_runs,
                            f_mean,
                            f_stderr,
                            f_relstderr,
                            t_runs,
                            t_mean,
                            t_stderr,
                            t_relstderr,
                        ) = get_f_t_statistics(filename)
                    except (IndexError, ValueError, FileNotFoundError) as e:
                        print(f"警告：处理文件 {filename} 时出错: {e}")
                        continue
                
                f.write(
                    f"{ll}, {gen}, {p_runs}, {p_mean}, {p_relstderr}, {f_runs}, {f_mean}, {f_relstderr}, {t_runs}, {t_mean}, {t_relstderr}\n"
                )


def write_f_t_results(res, gen, length, delay=False, is_triangle=False):
    triangle_dir = ""
    if is_triangle:
        triangle_dir = "_tr"
    del_dir = ""
    if delay:
        del_dir = "_del"
    filename = f"results{triangle_dir}{del_dir}/F_T_measure_{gen}_{length}.csv"
    mode = "w"
    i = 0
    if os.path.isfile(filename):
        mode = "a"
        with open(filename, "r") as fr:
            i = len(fr.readlines()) - 1
    with open(filename, mode) as fw:
        if mode == "w":
            fw.write("Run,F_meas,T_meas\n")
        i += 1
        for n, t in res:
            fw.write(f"{i},{n},{t}\n")
            i += 1


def write_p_results(res, gen, length, delay=False, is_triangle=False):
    triangle_dir = ""
    if is_triangle:
        triangle_dir = "_tr"
    del_dir = ""
    if delay:
        del_dir = "_del"
    filename = f"results{triangle_dir}{del_dir}/P_measure_{gen}_{length}.csv"
    mode = "w"
    i = 0
    if os.path.isfile(filename):
        mode = "a"
        with open(filename, "r") as fr:
            i = len(fr.readlines()) - 1
    with open(filename, mode) as fw:
        if mode == "w":
            fw.write("Run,P_meas\n")
        i += 1
        for p in res:
            fw.write(f"{i},{p}\n")
            i += 1


def fix_run_number(csv_file):
    with open(csv_file, "r") as fr:
        lines = fr.readlines()
    for i in range(1, len(lines)):
        lines[i] = re.sub(r"\d+,", f"{i},", lines[i], count=1)
    fw = open("new_" + csv_file, "w")
    fw.writelines(lines)
    fw.close()


def compare_P_meas(csv_file1, csv_file2):
    p1 = []
    p2 = []
    with open(csv_file1, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            # 添加错误处理：检查行是否有足够的列
            if len(r) >= 2:
                try:
                    p1.append(float(r[1]))
                except (ValueError, IndexError):
                    # 跳过格式错误的行
                    continue
            else:
                # 跳过列数不足的行
                continue
    
    with open(csv_file2, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            # 添加错误处理：检查行是否有足够的列
            if len(r) >= 2:
                try:
                    p2.append(float(r[1]))
                except (ValueError, IndexError):
                    # 跳过格式错误的行
                    continue
            else:
                # 跳过列数不足的行
                continue
    
    # 如果没有有效数据，返回默认值
    if len(p1) == 0 or len(p2) == 0:
        return 1.0  # 返回p-value=1.0表示无差异
    
    return ranksums(p1, p2).pvalue


def compare_F_T_meas(csv_file1, csv_file2):
    f1 = []
    t1 = []
    f2 = []
    t2 = []
    with open(csv_file1, "r") as f:
        reader = csv.reader(f)
        _ = next(reader)
        for r in reader:
            # 添加错误处理：检查行是否有足够的列
            if len(r) >= 3:
                try:
                    f1.append(float(r[1]))
                    t1.append(float(r[2]))
                except (ValueError, IndexError):
                    # 跳过格式错误的行
                    continue
            else:
                # 跳过列数不足的行
                continue
    
    with open(csv_file2, "r") as f:
        reader = csv.reader(f)
        _ = next(reader)
        for r in reader:
            # 添加错误处理：检查行是否有足够的列
            if len(r) >= 3:
                try:
                    f2.append(float(r[1]))
                    t2.append(float(r[2]))
                except (ValueError, IndexError):
                    # 跳过格式错误的行
                    continue
            else:
                # 跳过列数不足的行
                continue
    
    # 如果没有有效数据，返回默认值
    if len(f1) == 0 or len(f2) == 0 or len(t1) == 0 or len(t2) == 0:
        return 1.0, 1.0  # 返回p-value=1.0表示无差异
    
    return ranksums(f1, f2).pvalue, ranksums(t1, t2).pvalue
