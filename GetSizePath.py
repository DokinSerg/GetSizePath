import os
# import sys
# import uuid
import traceback
import asyncio
# import aiofiles
import aiofiles.os as aos
# from datetime import datetime,timezone,timedelta
from time import perf_counter
# from aioshutil import copy2 as Acopy2
from rich import print as rpn
#------------------------------------------
__author__ = 't.me/dokin_sergey'
__version__ = '0.0.11'
__verdate__ = '2025-05-07 15:19'
# SourcePath = r'c:\Users\dokin\AppData\Local\Yandex\YandexBrowser\User Data\Default'
semaphore = asyncio.Semaphore(7000)
WaitPrBar = True#ProgressBar Stop
# kGb = 1048576
kGb = 1024000
FileMaxSize:int = kGb
###############################################################################################################
async def progress_bar()-> None:
    i=0
    Delay = 1
    # Step = 10
    start_PrBr = perf_counter()
    # rpn('[',end = '')
    try:
        while WaitPrBar:
            await asyncio.sleep(Delay)
            # if   not i % Step:rpn(f'{int(i*Delay):0>3d}',end = '')
            if not i:
                rpn('[',end = '')
                i += 1
            elif not i % 60:rpn(f'[cyan1] {i:4}')
            elif not i % 2:rpn('[green1]+',end = '')
            else:rpn('[green1]-',end = '')
            i += 1
    finally:
        stop_PrBr = perf_counter()
        slep_time = round(stop_PrBr - start_PrBr,3)
        rpn(f'] по таймеру {slep_time}')
        # rpn(f'Задержка по таймеру {slep_time}')
##############################################################################################################
def InputMaxFile()->None:
    global FileMaxSize
    # FMS = kGb
    rpn('\t[cyan1]Файлы какого размера выводить на печать?')
    for nn in range(1,5):
        rpn(f'\t\t[green1]{nn} [cyan1]Больще [khaki1]{10**nn:6_} [cyan1]Мб')
    ##-------------------------------------------------------------------------
    ky = input('\t :->? ')
    if ky.isdigit() and int(ky) in range(1,5):
        FileMaxSize = kGb * 10 ** int(ky)
################################################################################################################
async def parsing_path(curpath:str)->tuple[str, int, int,dict[str,int]]:
    cursize = 0
    counfile = 0
    Filedict:dict[str,int] = {}
    try:
        async with semaphore:
            # rpn(f'[cyan1]{CurPath}')
            task_sa = []
            with await aos.scandir(curpath) as itPaths:
                for item in itPaths:
                    await asyncio.sleep(0)
                    if item.is_dir(follow_symlinks=False) and not item.is_junction():
                        # nextpaths.append(item.path)
                        task_a = asyncio.create_task(parsing_path(item.path))
                        task_sa.append(task_a)
                        await asyncio.sleep(0.01)
                        continue
                    if item.is_file(follow_symlinks=False):
                        counfile += 1
                        if (filesize := item.stat().st_size) > FileMaxSize:
                            Filedict[item.name] = filesize
                        cursize += filesize
        #--------------------------------------------------------
        await asyncio.gather(*task_sa)
        await asyncio.sleep(0)
    #--------------------------------------------------------
        for task in task_sa:
            counfile += task.result()[2]
            cursize += task.result()[1]
            Filedict.update(task.result()[3])
    #--------------------------------------------------------
    except PermissionError:
        await asyncio.sleep(0)
        # rpn(f'[khaki1]Отказано в доступе {CurPath}')
        # rpn(f'[khaki1]{CurPath}')
    except Exception as _err:
        rpn(f'[red1]PP:{_err}')
        rpn(f'[red1]PP:{traceback.format_exc()}')
    return curpath,cursize,counfile,Filedict
##############################################################################################################
async def main(source_path:str)->None:
    global WaitPrBar
    #-----------------------------------------------------------------------------
    while True:
        DirSize:dict[str,list[int]] = {}
        Filedict:dict[str,int] = {}
        DirFile:dict[str,dict[str,int]] = {}
        DirFile['root'] = {}
        all_size = 0
        CountFiles = 0
        RootCount  = 0
        # start_Src = perf_counter()
        try:
            tasks = []
            rpn(f'[cyan1]Расчет объёма директорий для > [green1]{source_path} [cyan1]<')
            WaitPrBar = True
            tsc = asyncio.create_task(progress_bar(),name='ProgressBar')
            with await aos.scandir(source_path) as itPaths:
                for item in itPaths:
                    await asyncio.sleep(0.01)
                    if item.is_dir(follow_symlinks=False) and not item.is_junction():
                        task = asyncio.create_task(parsing_path(item.path))
                        await asyncio.sleep(0)
                        tasks.append(task)
                        continue
                    if item.is_file(follow_symlinks=False):
                        CountFiles += 1
                        RootCount = CountFiles
                        if (filesize := item.stat().st_size) > FileMaxSize:
                            Filedict[item.name] = filesize
                            DirFile['root'].update(Filedict)
                        all_size += item.stat().st_size
        #--------------------------------------------------------------------------------------
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)
            # #--------------------------------------------------------------------------------
            for task in tasks:
                CountFiles += task.result()[2]
                all_size += task.result()[1]
                DirSize[task.result()[0]] = [task.result()[1],task.result()[2]]
                DirFile[task.result()[0]] = task.result()[3]
                # DirFile[task.result()[0]].update(task.result()[3])
        #--------------------------------------------------------------------------------------
            WaitPrBar = False
            await tsc
            if not tsc.done():
                tsc.get_coro().close()
            await asyncio.sleep(0.01)
        #--------------------------------------------------------------------------------------
        except Exception as err:
            rpn(f'[red1]Main:{err}')
            rpn(f'[red1]Main:{traceback.format_exc()}')
        #------------------------------------------------------------------------------------------
        sizekb = round(all_size/kGb,3)
        rpn()
        # rpn(f'[green1]{source_path}\n')
        sortDirSize = dict(sorted(DirSize.items(),key=lambda itm: itm[1][0],reverse=True))
    ##----------------------------------------------------------------------------------------
        rpn(f'{' '*10}[magenta1]Имя папки.файла {' '*60}:   Размер Мб :  кол-во')
        rpn(f'[magenta1]{'-'*109}')
        if DirFile['root']:
            rpn(f'[green1]   0 [cyan1]{source_path:74} [green1]{all_size:12_.3f} : {RootCount:7_}')
            if len(DirFile['root']) < 100:
                for fn,fs in DirFile['root'].items():
                    # rpn(f'    [khaki1] {fn:80} [cyan1]:{fs/kGb:12_.3f} :')
                    nff = '     ' + fn + ' ' * (81 - len(fn)) + ':'
                    print(nff,end = '')
                    rpn(f'[khaki1]{fs/kGb:12_.3f} :')
            else:
                rpn('\t[khaki1]Много файлов')
    ##---------------------------------------------------------------------------------------------
        for i,j in enumerate(sortDirSize.items(),start = 1):
            ipath = os.path.basename(j[0])
            fsn = f'{ipath[:80]} [khaki1]~' if len(ipath) > 80 else ipath
            rpn(f'[green1]{i:4} [cyan1]{fsn:81}:[green1]{j[1][0]/kGb:12_.3f} : {j[1][1]:7_}')
            if len(DirFile[j[0]]) >100:
                rpn('\t[khaki1]Много файлов')
                continue
            for fn,fs in DirFile[j[0]].items():
                base, ext = os.path.splitext(fn)
                ffn = f'{base[:74]}~{ext}' if len(base) > 74 else fn
                nff = '     ' + ffn + ' ' * (81 - len(ffn)) + ':'
                print(nff,end = '')
                rpn(f'[khaki1]{fs/kGb:12_.3f} :')
        rpn(f'\n[cyan1]Всего файлов [khaki1]{CountFiles:_} [cyan1]общим размером [khaki1]{all_size:_} [cyan1]байт ([khaki1]{sizekb:_} Mb)\n')
        # stop_Src = perf_counter()
        # FileListTime = round(stop_Src - start_Src,3)
        # rpn(f'Составление списка файлов заняло {FileListTime}c')
        rpn()
        #--------------------------------------------------------------------------------------
        while True:
            rpn('[cyan1]Введите номер папки. "0" возврат на уровень ввех')
            if not (kye := input('ENTER выход:-)> ')):return
            if kye =='0':
                source_path = os.path.dirname(source_path)
                break
            if kye.isdigit() and int(kye) <= len(sortDirSize):
                curDir = list(enumerate(sortDirSize))[int(kye)-1][1]
                source_path = os.path.join(source_path,curDir)
                rpn(source_path)
                break
        ##-------------------------------------------------------------------------------------
        rpn('-'*100)
        InputMaxFile()
###############################################################################################################
start_time = perf_counter()
StartPath = 'C:\\'
rpn('[cyan1]* Программа определения размера папок и "больших" файлов *')
rpn(f'[cyan1]Версия [green1]{__version__}[cyan1] от [green1]{__verdate__}[cyan1] автор [green1]{__author__}')
rpn(f'[cyan1]Введите "начальный путь" или букву диска. [ [green1]{StartPath} [cyan1]]', end = '')
while (key := input(' :-)> ')):
    if key =='0':os._exit(0)
    dr,_ = os.path.splitdrive(key)
    StartPath = f'{key}:' if not dr and len(key) == 1 else key
    ##------------------------------------------------
    if os.path.isdir(StartPath):break
    rpn(f'[cyan1]Путь [cyan1]{StartPath} [cyan1]не найден. Повторите ввод.')
##-------------------------------------------------------------------------
InputMaxFile()
asyncio.run(main(StartPath))
##-------------------------------------------------------------------------
input(':-> ')
os._exit(0)
