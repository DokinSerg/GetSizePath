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
__version__ = '0.0.9'
__verdate__ = '2025-05-06 18:22'
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
                    if item.is_dir(follow_symlinks=False):
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
        DirSize:dict[str,int] = {}
        Filedict:dict[str,int] = {}
        DirFile:dict[str,dict[str,int]] = {}
        DirFile['root'] = {}
        all_size = 0
        CountFiles = 0
        # start_Src = perf_counter()
        try:
            tasks = []
            rpn(f'Расчет объёма директорий для {source_path}')
            WaitPrBar = True
            tsc = asyncio.create_task(progress_bar(),name='ProgressBar')
            with await aos.scandir(source_path) as itPaths:
                for item in itPaths:
                    await asyncio.sleep(0.01)
                    if item.is_dir(follow_symlinks=False):
                        task = asyncio.create_task(parsing_path(item.path))
                        await asyncio.sleep(0)
                        tasks.append(task)
                        continue
                    if item.is_file(follow_symlinks=False):
                        CountFiles += 1
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
                DirSize[task.result()[0]] = task.result()[1]
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
        sortDirSize = dict(sorted(DirSize.items(),key=lambda itm: itm[1],reverse=True))
        Strlen = 30
    ##----------------------------------------------------------------------------------------
        if DirFile['root']:
            rpn(f'[green1]  0 [cyan1]{source_path:29} [green1]{all_size:12_.3f}')
            if len(DirFile['root']) < 100:
                for fn,fs in DirFile['root'].items():
                    rpn(f'\t[khaki1] {fn:42} [cyan1] {fs/kGb:12_.3f}')
            else:
                rpn('\t[khaki1]Много файлов')
    ##---------------------------------------------------------------------------------------------
        for i,j in enumerate(sortDirSize.items(),start = 1):
            ipath = os.path.basename(j[0])
            fsn = f'{ipath[:Strlen]} [khaki1]~' if len(ipath) > Strlen else ipath
            rpn(f'[green1]{i:3} [cyan1]{fsn:32} [green1]{j[1]/kGb:12_.3f}')
            if len(DirFile[j[0]]) >100:
                rpn('\t[khaki1]Много файлов')
                continue
            for fn,fs in DirFile[j[0]].items():
                rpn(f'\t[khaki1] {fn:42} [cyan1] {fs/kGb:12_.3f}')
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
rpn(f'[cyan1]Введите букву диска или [ [green1]{StartPath} [cyan1]]')
if not (key := input(' :-)> ')):
    key = StartPath
if key =='0':os._exit(0)
dr,_ = os.path.splitdrive(key)
if not dr: key = f'{key}:\\'
elif dr == StartPath:key = f'{key}\\'
##-------------------------------------------------------------------------
InputMaxFile()
asyncio.run(main(key))
##-------------------------------------------------------------------------
input(':-> ')
os._exit(0)
