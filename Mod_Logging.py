# pylint: disable-msg=W0603
import os,sqlite3,traceback,requests,inspect
from datetime import datetime,timezone,date,timedelta
from rich import print as rpn
__author__ = 't.me/dokin_sergey'
__version__ = '1.2.2'
__verdate__ = '2025-02-05 15:37'
_BaseName = 'OMC_Customer'
#----------------------------------------------------------------------------------------
_PROJECT = 'LogginModule'
_USERNAME = ''
_COMPNAME = str(os.environ['COMPUTERNAME'])
_COMP_PID = f'{os.getpid():4x}'
_GlobaLen = 120
#----------------------------------------------------------------------------------------
LogNetPath = r'\\more\copy\_log'
LogLocPath = r'C:\UserScripts\_log'
LogUsrPath = os.environ['USERPROFILE']
_debug_path = 'dev_log'
_SQLBaseRep = r'\\more\COPY\_log\_CentralStation\CentralReport.db3'
TOKEN = "6633397926:AAFIYCuBEXG09_n1kTyV-PxE7SiLi_1YU2s"
group_id = "839545749"
chat_id  = "-1002152529179"
#-----------------------------------------------------------------------------------------
_reportSQL = False
_FileNetLog = ''
_FileLocLog = ''
LogFileUsr = ''
debug = False
##################################################################################################################
def LoggingInit(PRJT:str = _debug_path,UsrNm:str = os.getlogin( ))->bool:
    global _PROJECT
    _PROJECT = PRJT
    global _USERNAME
    _USERNAME = UsrNm
    global _FileNetLog
    global _FileLocLog
    global LogFileUsr
    global _reportSQL
    #------------------------------------------------------------------------------------------------------------------------
    try:
        if os.path.isdir(LogNetPath):
            FileNetMod = os.path.join(LogNetPath,_debug_path) if PRJT != _BaseName else LogNetPath
            FileNetMod = os.path.join(FileNetMod,PRJT)
            if not os.path.isdir(FileNetMod):
                os.makedirs(FileNetMod)
            _FileNetLog = os.path.join(FileNetMod,f'{str(date.today())}.txt')
            if os.path.isfile(_FileNetLog) and not os.access(_FileNetLog, os.W_OK):
                _FileNetLog = os.path.join(FileNetMod,f'{str(date.today())}_.txt')
            with open(_FileNetLog, mode = 'a', encoding = 'utf_8') as sn:
                print('-' * (_GlobaLen + 50), file = sn)
        else:
            _FileNetLog = ''
    #------------------------------------------------------------------------------------------------------------------------
        if os.path.isdir(LogLocPath):
            FileLogMod = os.path.join(LogLocPath,_debug_path) if PRJT != _BaseName else LogLocPath
            FileLogMod = os.path.join(FileLogMod,PRJT)
            if not os.path.isdir(FileLogMod):
                os.makedirs(FileLogMod)
            _FileLocLog = os.path.join(FileLogMod,f'{str(date.today())}.txt')
            if os.path.isfile(_FileLocLog) and not os.access(_FileLocLog, os.W_OK):
                _FileLocLog = os.path.join(FileLogMod,f'{str(date.today())}_.txt')
            try:
                with open(_FileLocLog, mode = 'a', encoding = 'utf_8') as sl:
                    print('-' * (_GlobaLen + 50), file = sl)
            except PermissionError:
                for ifh in range(1,10):
                    _FileLocLog = os.path.join(FileLogMod,f'{str(date.today())}_{ifh}.txt')
                    try:
                        with open(_FileLocLog, mode = 'a', encoding = 'utf_8') as sl:
                            print('-' * (_GlobaLen + 50), file = sl)
                        break
                    except PermissionError:
                        continue
    #----------------------------------------------------------------------------------------------------
        try:
            if os.path.isdir(LogUsrPath):#Проверяем есть доступ в принципе или нет.
                LogFileUsr = os.path.join(LogUsrPath,'Documents')
                LogFileUsr = os.path.join(LogFileUsr,PRJT)
                if not os.path.isdir(LogFileUsr):os.makedirs(LogFileUsr,exist_ok=True)
                LogFileUsr = os.path.join(LogFileUsr,f'{str(date.today())}.txt')
                with open(LogFileUsr, mode = 'a', encoding = 'utf_8') as sn:
                    print('-' * _GlobaLen, file = sn)
            else:LogFileUsr = ''
        except OSError:
            LogFileUsr = ''
    #----------------------------------------------------------------------------------------------------
        LogErrDebug(f"Инициализация  модуля  логгирования ver: {__version__} ; от {__verdate__} ; автор {__author__}",os.path.basename(__file__))
        _reportSQL = ReportSQLiteStart(PRJT)
#--------------------------------------------------------------------------------------------------------
    except Exception as Err:
        Lini = False
        rpn(str(Err))
    else:
        Lini = True
        # print(f'R_sql:{sqlite3.sqlite_version = } : {TabName =}')
    return Lini
##################################################################################################################
def TgBotMess(_TgStr:str,dbg:bool = False)->bool:
    res = True
    try:
        _chat_id = chat_id if dbg else group_id#При отладке отправляем только себе, при ошибке - в группу
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={_chat_id}&text={_TgStr}"
        requests.get(url, timeout=15).json()
    except Exception as _ErrMs:
        res = False
        LogErrDebug('ErrMess',f'{_ErrMs}','TgBotMess')
        LogErrDebug('ErrTrac',f'{traceback.format_exc()}','TgBotMess')
    return res
##################################################################################################################
def ReportSQLiteStart(TabName:str  = _PROJECT)->bool:
    # print(f'0:{_PROJECT = }')
    IB = None
    try:
        with sqlite3.connect( _SQLBaseRep ) as conn:
            sql_txt = "CREATE TABLE IF NOT EXISTS " + TabName
            sql_txt = sql_txt + """ (
                    iDate DATE DEFAULT (date('now')) NOT NULL,
                    iTime TIME DEFAULT (time('now','+3 hours')) NOT NULL,
                    IdOmcdUser TEXT DEFAULT (''),
                    iTermOrOU  TEXT DEFAULT (''),
                    iAction    TEXT DEFAULT (''),
                    iUserName TEXT DEFAULT ('TechoMod'),
                    iCompName TEXT DEFAULT ('localhost'),
                    iD INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL)
                    ;"""
            curs = conn.execute(sql_txt)
            sql_txt = "SELECT name FROM sqlite_master Where name = '" + TabName + "'"
            res = curs.execute(sql_txt)
            res.fetchone()
    except sqlite3.Warning as Warn:
        LogErrDebug(str(Warn),'NewSQLiteSession')
        IB = False
    except sqlite3.Error as DErr:
        LogErrDebug(str(DErr),'NewSQLiteSession')
        IB = False
    else:
        IB = True
        LogErrDebug(f"Инициализация SQL документирования: SQLite {sqlite3.sqlite_version} ; {TabName} ; {_SQLBaseRep}",'NewSQLiteSession')
    return IB
##################################################################################################################
def ReportSql(IdOmcdUser:str, iTermOrOU:str,iAction:str, TabName:str = _PROJECT)->bool:
    if TabName != _PROJECT: TabName = _PROJECT
    # print(f'{TabName = } : {IdOmcdUser = } ; {iTermOrOU = } ; {iAction = }')
    if not _reportSQL: return False
    #-------------------------------------------------------------------- Усли это OU то отрезаем Домен
    iTrOu = iTermOrOU.rsplit(',',2)[0] if ',' in iTermOrOU else iTermOrOU
    #--------------------------------------------------------------------------
    IB = False
    try:
        with sqlite3.connect(_SQLBaseRep) as conn:
            sql_txt  = f'INSERT INTO {TabName} (IdOmcdUser,iTermOrOU,iAction,iUserName,iCompName)\n'
            sql_txt += "VALUES (?,?,?,?,?)"
            DataS = (IdOmcdUser,iTrOu,iAction,_USERNAME,_COMPNAME)
            conn.execute(sql_txt, DataS)
    except sqlite3.Warning as Warn:
        LogErrDebug(str(Warn),'WriteSql')
        IB = False
    except sqlite3.Error as DErr:
        LogErrDebug(str(DErr),'WriteSql')
        IB = False
    else:
        IB = True
        # print(f'R_sql:{sqlite3.sqlite_version = } : {TabName =}')
    return IB

##################################################################################################################
def WordRead(Wrd:str)->bool:
    Wres = False
    if   Wrd.isalnum():
        Wres = True
    else:
        for iw in Wrd:
            if (ord(iw) in range(33,125)) or (ord(iw) in range(192,255)):
                Wres = True
                break
    return Wres
##################################################################################################################
def LogErrDebug(Mess1:str,Mess2:str, Mess3:str = '')->bool:
    TypeMess = ('Message','Success','Warning','ErrMess','ErrTrac','ErrPoSh','psstrlg','ErroCMD')#Caution
    # print(f'{_PROJECT =};{_FileNetLog = };{_FileLocLog = };{_FileUsrLog = };{_reportSQL}{''}{''} ')
    if len(Mess1) == 7 and Mess1 in TypeMess:
        TMess = Mess1#+' '
        RMess = Mess2
    else:
        TMess = 'Message'
        RMess = Mess1
    Funct = Mess3 if Mess3 else inspect.stack()[1][3]
    ListMess = []
    try:
        dtnow = datetime.now(timezone.utc) + timedelta(hours=3)
        dtstr = dtnow.strftime("%H:%M:%S")
        NetStr = f'{dtstr};{_USERNAME:12};{TMess};{_COMPNAME};'
        MesStr = f'{dtstr};{_USERNAME:12};{TMess};'
        PrnStr = f'{dtstr};{TMess};'
        lFN = 17
        FN = f'{Funct:{lFN}} ;' if Funct else f'{" ":{lFN}} ;'
        MesStr += FN
        PrnStr += FN
        NetStr += FN
        #------------------------------------------------------------------------------------------
        TgStr = f'Компьютер: {_COMPNAME}\nПользователь: {_USERNAME}\nФункция: {Funct}\n{RMess}'
        #------------------------------------------------------------------------------------------
        # ListStr = RawMess.splitlines() if isinstance(RawMess,str) else str(RawMess).splitlines()
        if TMess in ('Warning','ErrMess','Success','Message'):
            ListStr = str(RMess).splitlines()
            # print(ListStr)
            tstr = ''
            for iStr in ListStr:
                if iStr and not iStr.isspace():
                    ListWr = iStr.split()
                    for iLW in ListWr:
                        if iLW and WordRead(iLW):
                            tstr += f' {iLW}'
                        if len(tstr) >_GlobaLen:
                            # print(tstr)
                            ListMess.append(tstr)
                            tstr = ''
            if tstr: ListMess.append(tstr)
            #--------------------------------------------------------------------
            if _FileNetLog:
                with open(_FileNetLog, mode = 'a', encoding = 'utf_8') as fh:
                    for ims in ListMess:
                        print(f'{NetStr}{ims}', file = fh)
            #-----------------------------------------------------------------------
            if _FileLocLog:
                with open(_FileLocLog, mode = 'a', encoding = 'utf_8') as fl:
                    for ims in ListMess:
                        print(f'{MesStr}{ims}', file = fl)
            #-----------------------------------------------------------------------
            if LogFileUsr:
                with open(LogFileUsr, mode = 'a', encoding = 'utf_8') as fl:
                    for ims in ListMess:
                        print(f'{PrnStr}{ims}', file = fl)
        #-----------------------------------------------------------------------------
        else:
            if _FileNetLog:
                with open(_FileNetLog, mode = 'a', encoding = 'utf_8') as fh:
                    print(NetStr, file = fh)
                    print(RMess, file = fh)
            #-----------------------------------------------------------------------
            if _FileLocLog:
                with open(_FileLocLog, mode = 'a', encoding = 'utf_8') as fl:
                    print(MesStr, file = fl)
                    for wstr in RMess.splitlines():
                        print(wstr, file = fl)
            #-----------------------------------------------------------------------
            if LogFileUsr:
                with open(LogFileUsr, mode = 'a', encoding = 'utf_8') as fl:
                    print(MesStr, file = fl)
                    for wstr in RMess.splitlines():
                        print(wstr, file = fl)
       #--------------------------------------------------------------------
        if TMess in ('ErrMess','ErroCMD'):#,'ErrPoSh'
            # url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={TgStr}"
            # jsonstr = requests.get(url, timeout=15).json()
            TgBotMess(TgStr)
        #---------------------------------------------------------------------------------------------------------------------------
        if debug or not _FileLocLog:
            rpn(f'[yellow]{PrnStr}{RMess}')
        #---------------------------------------------------------------------------------------------------------------------------
        # if Modul and _FileUsrLog:
            # with open(_FileUsrLog, mode = 'a', encoding = 'utf_8') as fl:
                # for ims in ListMess:
                    # print( ims)
                    # print(f'{MesStr}{ims}', file = fl)
    except Exception as Err:
        Led = False
        if debug:rpn(str(Err))
    else:
        Led = True
    return Led
##################################################################################################################
def tg_group_test(_TgStr:str,)->bool:
    res = True
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={group_id}&text={_TgStr}"
        _ar = requests.get(url, timeout=15).json()
        # rpn(_ar)
    except Exception as _ErrMs:
        res = False
        LogErrDebug('ErrMess',f'{_ErrMs}','TgBotMess')
        LogErrDebug('ErrTrac',f'{traceback.format_exc()}','TgBotMess')
    return res
##################################################################################################################
if __name__ == '__main__':
    debug = True
    print(f"Автономный Тест модуля логгирования: {os.path.basename(__file__)} ver: {__version__} от {__verdate__} автор {__author__}")
    _,PROJECT = os.path.split(__file__)
    PROJECT,_ = os.path.splitext(PROJECT)
    ProjUser = os.getlogin()
    LoggingInit(PROJECT,ProjUser)
    print(f'{_FileNetLog = }')
    print(f'{_FileLocLog = }')
    print(f'{LogFileUsr = }')
    # ReportSql('dev24001','OU=Clients-DEV,DC=1more,DC=cloud','Edit')
    LogErrDebug('Message',f"Автономный Тест модуля логгирования: {__version__} ; от {__verdate__} ; автор {__author__}")
    # LogErrDebug('Message',"Проверка сохранения длинных и многострочных строк с разбивкой на удочитаемы клочки и паттерны, а также прочей ерунды для удоства использования",os.path.basename(__file__))
    # LogErrDebug('ErrTrac'," Мой дядя самых честных правил,\n когда не в шутку занемог\n он уважать себя заставил\n и лучше выдумать не мог\n",os.path.basename(__file__))
    # LogErrDebug('ErrMess'," Мой дядя самых честных правил,\n когда не в шутку занемог\n он уважать себя заставил\n и лучше выдумать не мог\n",os.path.basename(__file__))
    # LogErrDebug(Messeg, __name__, _MODNAME)
    # LogErrDebug('Текст простой обычной строки for exampl для проверки правильности написание различных тестов: и прочих проверок! и различных вариантов ', __name__)
    ancl = " Мой дядя самых честных правил,\n когда не в шутку занемог\n он уважать себя заставил\n и лучше выдумать не мог\n"
    tg_group_test(ancl)
else:
    debug = False
    # LogErrDebug(f"Инициализация модуля логгирования ver: {_VERSION} ; от {_VERDATE} ; автор {_AUTHOR}",os.path.basename(__file__))
