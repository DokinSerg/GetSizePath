import os
import sys
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
__version__ = '0.0.-3'
__verdate__ = '2025-04-17 13:59'
SourcePath = r'C:\Dev'
semaphore = asyncio.Semaphore(500)
WaitPrBar = True#ProgressBar Stop
kGb = 1048576
###############################################################################################################
async def ProgressBar()-> None:
    i=0
    Delay = 1
    # Step = 10
    start_PrBr = perf_counter()
    rpn('[',end = '')
    try:
        while WaitPrBar:
            i += 1
            # if   not i % Step:rpn(f'{int(i*Delay):0>3d}',end = '')
            if not i % 2:rpn('[green1]+',end = '')
            else:rpn('[green1]-',end = '')
            await asyncio.sleep(Delay)
    finally:
        stop_PrBr = perf_counter()
        slep_time = round(stop_PrBr - start_PrBr,3)
        rpn(']', f'{slep_time}')
##############################################################################################################
##############################################################################################################
################################################################################################################
async def ParsingPath(CurPath:str)->tuple[str, int, int]:
    cursize = 0
    counfile = 0
    # rpn(f'1: {CurPath = }')
    CurListPath = [CurPath]
    await asyncio.sleep(0.01)
    try:
        async with semaphore:
            while CurListPath:
                nextpaths = []
                for ipath in CurListPath:
                    with await aos.scandir(ipath) as itPaths:
                        for item in itPaths:
                            await asyncio.sleep(0.01)
                            if item.is_dir():
                                nextpaths.append(item.path)
                                continue
                            if item.is_file():
                                counfile += 1
                                cursize += item.stat().st_size
                #--------------------------------------------------------
                CurListPath = nextpaths
    #--------------------------------------------------------
    except Exception as _err:
        rpn(f'[red1]PP:{_err}')
        rpn(f'[red1]PP:{traceback.format_exc()}')
    return CurPath,cursize,counfile
##############################################################################################################
async def main()-> None:
    global WaitPrBar
    DirSize:dict[str,int] = {}
    all_size = 0
    pathlist = []
    CountFiles = 0
    try:
        tasks = []
        rpn('Подготовка списка файлов')
        start_Src = perf_counter()
        WaitPrBar = True
        tsc = asyncio.create_task(ProgressBar(),name='ProgressBar')
        with await aos.scandir(SourcePath) as itPaths:
            for item in itPaths:
                await asyncio.sleep(0.01)
                if item.is_dir():
                    pathlist.append(item.path)
                    tasks.append(asyncio.create_task(ParsingPath(item.path)))
                    continue
                if item.is_file():
                    CountFiles += 1
                    all_size += item.stat().st_size
    #--------------------------------------------------------------------------------------
        # tasks = [asyncio.create_task(ParsingPath(Item)) for Item in pathlist]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.01)
        # #--------------------------------------------------------------------------------
        for task in tasks:
            CountFiles += task.result()[2]
            all_size += task.result()[1]
            DirSize[task.result()[0]]  = task.result()[1]
    #--------------------------------------------------------------------------------------
        WaitPrBar = False
        await tsc
        if not tsc.done():tsc.get_coro().close()
        await asyncio.sleep(0.01)
    #--------------------------------------------------------------------------------------
        sizekb = round(all_size/kGb,3)
        rpn()
        for i,j in DirSize.items():
            rpn(f'[turquoise2]{i:40} [green1]{round(j/kGb,3):10}')
        rpn(f'[turquoise2]Всего файлов [green1]{CountFiles} [turquoise2]общим размером [green1]{all_size} [turquoise2]байт ([green1]{sizekb} Mb)\n')
        stop_Src = perf_counter()
        FileListTime = round(stop_Src - start_Src,3)
        rpn(f'Составление списка файлов заняло {FileListTime}c')
    #--------------------------------------------------------------------------------------
        # rpn(f'Запись протокола в {LogUsrFile}')
        # WaitPrBar = True
        # PrBar = asyncio.create_task(ProgressBar())
        # LogLines:list[str] = []
        # for Ctsk in copytasks:
            # LogLines += Ctsk.result()
        # if MessList:#Записываем  хвост протокола
            # await Loglines()
        # WaitPrBar = False
        # await PrBar
        # if not PrBar.done():PrBar.get_coro().close()
        #-----------------------------------------------------------------------------
        # await asyncio.create_task(LogMessage(f'Копирование завершено. Скопировано {len(FileList)} файлов. Время копирования {copy_time} c'))
        # await asyncio.sleep(0.1)
    #-------------------------------------------------------------------------------------
    except Exception as err:
        rpn(f'[red1]Main:{err}')
        rpn(f'[red1]Main:{traceback.format_exc()}')
###############################################################################################################
start_time = perf_counter()
asyncio.run(main())
stop_time = perf_counter()
Inetrval = stop_time - start_time
print(f'\nОбщее время выполнения {Inetrval:.7f}')
if not (len(sys.argv) > 1 and sys.argv[1] == 'cons'):input(':-> ')
os._exit(0)
