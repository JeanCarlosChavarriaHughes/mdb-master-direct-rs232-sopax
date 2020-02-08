import socket
import sys
import serial
import os
import time
import json
import string

def dump_message(_lmessage):
    _ldebug_string = ""
    for _li in range(0,len(_lmessage)):
        _tmp_string = hex(_lmessage[_li])[2:]
        if len(_tmp_string) == 1:
            _ldebug_string = "0"+_tmp_string+" "
        else:
            _ldebug_string += _tmp_string + " "
    print(_ldebug_string)

# verify the length and the CRC on received message
def mdb_check_received_string(_lser,_lsock,_llsir):
    print(_llsir)
    if len(_llsir)>3:
        _lcrc=0
        for _li in range(0,len(_llsir)-1):
            _lcrc=_lcrc ^ _llsir[_li]
        if _lcrc==_llsir[len(_llsir)-1]:
            return 1
        else:
            _lser.timeout = 0.5
            _tmp_clean_buffer = _lser.read(100)
            return 2
    else:
        return 3
    
# MDB bill validator INIT
def mdb_bill_init(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x42,0x01,0xBD]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBBIllInit" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBBIllInit" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBBIllInit" : "failed"}).encode()+b"\n")
        return False

# MDB bill validator ENABLE
def mdb_bill_enable(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x42,0x02,0xBE]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBBIllEnable" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBBIllEnable" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBBIllEnable" : "failed"}).encode()+b"\n")
        return False

# MDB bill validator DISABLE
def mdb_bill_disable(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x42,0x03,0xBF]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBBIllDisable" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBBIllDisable" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBBIllDisable" : "failed"}).encode()+b"\n")
        return False

# MDB get INTERNAL SETTINGS from bill validator
def mdb_bill_get_settings(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x42,0x04,0xB8]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(60)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if len(_ltmp_string)>58:
            _ljson_string='{"Type": "BillSettigs",'
            _lfeature_level=str(_ltmp_string[3])
            _lcountry_code=hex((_ltmp_string[4]*256)+_ltmp_string[5])
            _lscaling_factor=str((_ltmp_string[6]*256)+_ltmp_string[7])
            _ldecimal_places=str(_ltmp_string[8])
            _lstacker_capacity=str((_ltmp_string[9]*256)+_ltmp_string[10])
            if _ltmp_string[13]==0xFF:
                _lescrow_available="True"
            else:
                _lescrow_available="False"
            _lbill_values=[]
            for _li in range(14,30):
                _lbill_values.append(str(_ltmp_string[_li]))
            _lmanufacturer=_ltmp_string[30:33].decode()
            _lserial_number=_ltmp_string[33:45].decode()
            _lserial_model=_ltmp_string[45:57].decode()
            _lsoftware_version=str((_ltmp_string[57]*256)+_ltmp_string[58])
            
            
            
            _ljson_string+='"level": "'+_lfeature_level+'",'
            _ljson_string+='"CurrencyCode": "'+_lcountry_code[2:]+'",'
            _ljson_string+='"ScalingFactor": "'+_lscaling_factor+'",'
            _ljson_string+='"DecimalPlaces": "'+_ldecimal_places+'",'
            _ljson_string+='"StackerCapacity": "'+_lstacker_capacity+'",'
            _ljson_string+='"EscrowAvailable": "'+_lescrow_available+'",'
            _ljson_string+='"BillValues":['
            for _li in range(0,len(_lbill_values)-1):
                _ljson_string+='{"BillValue": "'+_lbill_values[_li]+'"},'
            _ljson_string+='{"BillValue": "'+_lbill_values[_li]+'"}],'
            _ljson_string+='"Manufacturer": "'+_lmanufacturer+'",'
            _ljson_string+='"SerialNumber": "'+_lserial_number+'",'
            _ljson_string+='"Model": "'+_lserial_model+'",'
            _ljson_string+='"SWVersion": "'+_lsoftware_version+'"'
            _ljson_string+='}\n'
            _lsock.send(_ljson_string.encode())
            return True
        else:
            return False
    else:
        #print("CRC fail")
        return False

# MDB coin acceptor INIT
def mdb_coin_init(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x43,0x01,0xBC]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCoinInit" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCoinInit" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCoinInit" : "failed"}).encode()+b"\n")
        return False   

# MDB coin acceptor ENABLE
def mdb_coin_enable(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x43,0x02,0xBF]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCoinEnable" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCoinEnable" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCoinEnable" : "failed"}).encode()+b"\n")
        return False
    
# MDB coin acceptor DISABLE
def mdb_coin_disable(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x43,0x03,0xBE]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCoinDisable" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCoinDisable" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCoinDisable" : "failed"}).encode()+b"\n")
        return False
    
    
# MDB get INTERNAL SETTINGS from coin acceptor
def mdb_coin_get_settings(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x43,0x04,0xB9]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(60)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if len(_ltmp_string)>58:
            _ljson_string='{"Type": "CoinSettigs",'
            _lfeature_level=str(_ltmp_string[3])
            _lcountry_code=hex((_ltmp_string[4]*256)+_ltmp_string[5])
            _lscaling_factor=str(_ltmp_string[6])
            _ldecimal_places=str(_ltmp_string[7])
            _lcoin_values=[]
            for _li in range(10,26):
                if _ltmp_string[_li]==0xFF:
                    _lcoin_values.append("Token")
                elif _ltmp_string[_li]==0x20:
                    _lcoin_values.append("N/A")
                else:
                    _lcoin_values.append(str(_ltmp_string[_li]))
            _lmanufacturer=_ltmp_string[26:29].decode()
            _lserial_number=_ltmp_string[29:41].decode()
            _lserial_model=_ltmp_string[41:53].decode()
            _lsoftware_version=str((_ltmp_string[53]*256)+_ltmp_string[54])
            
            _ljson_string+='"level": "'+_lfeature_level+'",'
            _ljson_string+='"CurrencyCode": "'+_lcountry_code[2:]+'",'
            _ljson_string+='"ScalingFactor": "'+_lscaling_factor+'",'
            _ljson_string+='"DecimalPlaces": "'+_ldecimal_places+'",'
            _ljson_string+='"CoinValues":['
            for _li in range(0,len(_lcoin_values)-1):
                _ljson_string+='{"CoinValue": "'+_lcoin_values[_li]+'"},'
            _ljson_string+='{"CoinValue": "'+_lcoin_values[_li]+'"}],'
            _ljson_string+='"Manufacturer": "'+_lmanufacturer+'",'
            _ljson_string+='"SerialNumber": "'+_lserial_number+'",'
            _ljson_string+='"Model": "'+_lserial_model+'",'
            _ljson_string+='"SWVersion": "'+_lsoftware_version+'"'
            _ljson_string+='}\n'
            _lsock.send(_ljson_string.encode())
            return True
        else:
            return False
    else:
        #print("CRC fail")
        return False
    
# MDB set max credit commit
def mdb_set_max_credit(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBSetMaxCredit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lmax_credit=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBSetMaxCredit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x52,0x01]
    _lmask=0xFF000000
    _ldeplasament=24
    for _li in range(0,4):
        _ltmp_byte=_lmax_credit & _lmask
        _ltmp_byte = _ltmp_byte >> _ldeplasament
        _ltmp_string.append(_ltmp_byte)
        _lmask=_lmask >> 8
        _ldeplasament = _ldeplasament - 8
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBSetMaxCredit" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBSetMaxCredit" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBSetMaxCredit" : "failed"}).encode()+b"\n")
        return False
    
# MDB set change commit
def mdb_set_change(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBSetChange": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lmax_credit=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBSetChange": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    _lser.timeout=2
    _ltmp_string=[0xFE,0x52,0x03]
    _lmask=0xFF000000
    _ldeplasament=24
    for _li in range(0,4):
        _ltmp_byte=_lmax_credit & _lmask
        _ltmp_byte = _ltmp_byte >> _ldeplasament
        _ltmp_string.append(_ltmp_byte)
        _lmask=_lmask >> 8
        _ldeplasament = _ldeplasament - 8
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBSetChange" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBSetChange" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBSetChange" : "failed"}).encode()+b"\n")
        return False
    
# MDB reset current credit
def mdb_credit_reset(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x52,0x02,0xAE]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCreditReset" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCreditReset" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCreditReset" : "failed"}).encode()+b"\n")
        return False
    
# MDB set current credit
def mdb_set_current_credit(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBSetCurrentCredit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcurrent_credit=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBSetCurrentCredit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False

    _lser.timeout=2
    _ltmp_string=[0xFE,0x52,0x04]
    _lmask=0xFF000000
    _ldeplasament=24
    for _li in range(0,4):
        _ltmp_byte=_lcurrent_credit & _lmask
        _ltmp_byte = _ltmp_byte >> _ldeplasament
        _ltmp_string.append(_ltmp_byte)
        _lmask=_lmask >> 8
        _ldeplasament = _ldeplasament - 8
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBSetCurrentCredit" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBSetCurrentCredit" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBSetCurrentCredit" : "failed"}).encode()+b"\n")
        return False
 
# MDB POLL
def mdb_poll(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x50,0x01,0xAF]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(36)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if len(_ltmp_string)>31:
            _ljson_string='{"Type": "Poll",'
            _lcurrent_credit_cash=0
            for _li in range(3,7):
                _lcurrent_credit_cash=_lcurrent_credit_cash << 8
                _lcurrent_credit_cash = _lcurrent_credit_cash + _ltmp_string[_li]
            _lcurrent_credit_cashless=0
            for _li in range(7,11):
                _lcurrent_credit_cashless=_lcurrent_credit_cashless << 8
                _lcurrent_credit_cashless = _lcurrent_credit_cashless + _ltmp_string[_li]
            _lbill_stat = ""
            _lbill_stat_value=0
            for _li in range(11,15):
                _lbill_stat_value=_ltmp_string[_li]
                if _lbill_stat_value<10:
                    _lbill_stat+="0"+hex(_lbill_stat_value)[2:]
                else:
                    _lbill_stat+=hex(_lbill_stat_value)[2:]
            _lcoin_stat = ""
            _lcoin_stat_value=0
            for _li in range(15,19):
                _lcoin_stat_value=_ltmp_string[_li]
                if _lcoin_stat_value<10:
                    _lcoin_stat+="0"+hex(_lcoin_stat_value)[2:]
                else:
                    _lcoin_stat+=hex(_lcoin_stat_value)[2:]
            _lcashless_stat = ""
            _lcashless_stat_value=0
            for _li in range(19,23):
                _lcashless_stat_value=_ltmp_string[_li]
                if _lcashless_stat_value<10:
                    _lcashless_stat+="0"+hex(_lcashless_stat_value)[2:]
                else:
                    _lcashless_stat+=hex(_lcashless_stat_value)[2:]
            _lcashless_id = ""
            _lcashless_id_value=0
            for _li in range(27,31):
                _lcashless_id_value=_ltmp_string[_li]
                if _lcashless_id_value<10:
                    _lcashless_id+="0"+hex(_lcashless_id_value)[2:]
                else:
                    _lcashless_id+=hex(_lcashless_id_value)[2:]
            _lmax_available_change=0
            for _li in range(31,35):
                _lmax_available_change=_lmax_available_change << 8
                _lmax_available_change += _ltmp_string[_li]            
 
            _ljson_string+='"CurrentCreditCash": "'+str(_lcurrent_credit_cash)+'",'
            _ljson_string+='"CurrentCreditCashless": "'+str(_lcurrent_credit_cashless)+'",'
            _ljson_string+='"BillStat": "'+_lbill_stat+'",'
            _ljson_string+='"CoinStat": "'+_lcoin_stat+'",'
            _ljson_string+='"CashlessStat": "'+_lcashless_stat+'",'
            _ljson_string+='"CashlessID": "'+_lcashless_id+'",'
            _ljson_string+='"AvailableChange": "'+str(_lmax_available_change)+'"'
            _ljson_string+='}\n'
            _lsock.send(_ljson_string.encode())
            return True
        else:
            return False
    else:
        _lsock.send(json.dumps({"MDBPoll" : "failed"}).encode()+b"\n")
        return False
    
# MDB reset PMS statuses
def mdb_reset_status(_lser,_lsock,_lsir):
    _lser.timeout=2
    _ltmp_string=[0xFE,0x50,0x02,0xAC]
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBResetStatus" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBResetStatus" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBResetStatus" : "failed"}).encode()+b"\n")
        return False

# MDB cashless INIT
def mdb_cashless_init(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessInit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessInit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessInit": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x01]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessInit" : "success"}).encode()+b"\r\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessInit" : "failed"}).encode()+b"\r\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessInit" : "failed"}).encode()+b"\r\n")
        return False    
    return True
        
# MDB cashless ENABLE
def mdb_cashless_enable(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessEnable": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessEnable": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessEnable": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x02]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessEnable" : "success"}).encode()+b"\r\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessEnable" : "failed"}).encode()+b"\r\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessEnable" : "failed"}).encode()+b"\r\n")
        return False    
    return True

# MDB cashless DISABLE
def mdb_cashless_disable(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessDisable": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessDisable": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessDisable": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x03]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessDisable" : "success"}).encode()+b"\r\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessDisable" : "failed"}).encode()+b"\r\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessDisable" : "failed"}).encode()+b"\r\n")
        return False    
    return True

# MDB cashless VEDND CANCEL
def mdb_cashless_vend_cancel(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessVendCancel": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessVendCancel: "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessVendCancel": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x04]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessVendCancel" : "success"}).encode()+b"\r\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessVendCancel" : "failed"}).encode()+b"\r\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessVendCancel" : "failed"}).encode()+b"\r\n")
        return False    
    return True

# MDB send cashless vend request
def mdb_cashless_vend_request(_lser,_lsock,_lsir):
    # extract cashless number
    _start = _lsir.find("(")
    _end = _lsir.find(",",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessVendRequest": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessVendRequest: "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessVendRequest": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False

    # extracting product price
    _start = _lsir.find(",",_end)
    _end = _lsir.find(",",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        return False       
    try:
        _lproduct_price = int(_lsir[_start + 1:_end])
    except:
        print("Non-numeric price")
        return False

   # extracting product number
    _start = _lsir.find(",",_end)
    _end = _lsir.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        return False       
    try:
        _lproduct_number = int(_lsir[_start + 1:_end])
    except:
        print("Non-numeric product number")
        return False 
  
    _ltmp_string=[0xFE,0x53,0x05]
    _ltmp_string.append(_lcashless_number)
    # append product price
    _lmask=0xFF000000
    _ldeplasament=24
    for _li in range(0,4):
        _ltmp_byte=_lproduct_price & _lmask
        _ltmp_byte = _ltmp_byte >> _ldeplasament
        _ltmp_string.append(_ltmp_byte)
        _lmask=_lmask >> 8
        _ldeplasament = _ldeplasament - 8
    
    # append product number
    _lmask=0xFF00
    _ldeplasament=8
    for _li in range(0,2):
        _ltmp_byte=_lproduct_number & _lmask
        _ltmp_byte = _ltmp_byte >> _ldeplasament
        _ltmp_string.append(_ltmp_byte)
        _lmask=_lmask >> 8
        _ldeplasament = _ldeplasament - 8

    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    print(_ltmp_string)
    _lser.timeout=2
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessVendRequest" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessVendRequest" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessVendRequest" : "failed"}).encode()+b"\n")
        return False
    
# MDB cashless VEDND SUCCESS
def mdb_cashless_vend_success(_lser,_lsock,_lsir):
    # extract cashless number
    _start = _lsir.find("(")
    _end = _lsir.find(",",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessVendSuccess": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessVendSuccess: "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessVendSuccess": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
   # extracting product number
    _start = _lsir.find(",",_end)
    _end = _lsir.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        return False       
    try:
        _lproduct_number = int(_lsir[_start + 1:_end])
    except:
        print("Non-numeric product number")
        return False 
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x06]
    _ltmp_string.append(_lcashless_number)
    
    # append product number
    _lmask=0xFF00
    _ldeplasament=8
    for _li in range(0,2):
        _ltmp_byte=_lproduct_number & _lmask
        _ltmp_byte = _ltmp_byte >> _ldeplasament
        _ltmp_string.append(_ltmp_byte)
        _lmask=_lmask >> 8
        _ldeplasament = _ldeplasament - 8
    _lcrc=0
    
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessVendSuccess" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessVendSuccess" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessVendSuccess" : "failed"}).encode()+b"\n")
        return False    
    return True

# MDB cashless VEDND FAILED
def mdb_cashless_vend_failed(_lser,_lsock,_lsir):
    # extract cashless number
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessVendFailed": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessVendFailed: "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessVendFailed": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x07]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessVendFailed" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessVendFailed" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessVendFailed" : "failed"}).encode()+b"\n")
        return False    
    return True

# MDB cashless REVALUE
def mdb_cashless_revalue(_lser,_lsock,_lsir):
    # extract cashless number
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessRevalue": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessRevalue: "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessRevalue": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False

    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x08]
    _ltmp_string.append(_lcashless_number)
    
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    print(_ltmp_string)
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessRevalue" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessRevalue" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessRevalue" : "failed"}).encode()+b"\n")
        return False    
    return True

# MDB cashless END SESSION
def mdb_cashless_end_session(_llinput):
    # extract cashless number
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessEndSession": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessEndSession: "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessEndSession": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    
    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x0A]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)
    _lser.write(_ltmp_string)
    _ltmp_string=ser.read(5)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if _ltmp_string[3]==0xFC:
            _lsock.send(json.dumps({"MDBCashlessEndSession" : "success"}).encode()+b"\n")
            return True
        else:
            _lsock.send(json.dumps({"MDBCashlessEndSession" : "failed"}).encode()+b"\n")
            return False
    else:
        _lsock.send(json.dumps({"MDBCashlessEndSession" : "failed"}).encode()+b"\n")
        return False    
    return True

# MDB get INTERNAL SETTINGS from cashless
def mdb_cashless_get_settings(_lser,_lsock,_lsir):
    _start = _lsir.find("(")
    _end = _lsir.find(")",_start)
    if (_start == -1) | (_end == -1):
        _ljson_string='{"MDBCashlessGetSettings": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    try:
        _lcashless_number=int(_lsir[_start+1:_end])
    except:
        _ljson_string='{"MDBCashlessGetSettings": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False
    if (_lcashless_number!=1) & (_lcashless_number!=2):
        _ljson_string='{"MDBCashlessGetSettings": "failed"}\r\n'
        _lsock.send(_ljson_string.encode())
        return False

    _lser.timeout=2
    _ltmp_string=[0xFE,0x53,0x09]
    _ltmp_string.append(_lcashless_number)
    _lcrc=0
    for _li in range(0,len(_ltmp_string)):
        _lcrc=_lcrc ^ _ltmp_string[_li]
    _ltmp_string.append(_lcrc)    
    _lser.write(_ltmp_string)
    _ltmp_string=_lser.read(42)
    if mdb_check_received_string(_lser,_lsock,_ltmp_string)==1:
        if len(_ltmp_string)>41:
            _ljson_string='{"Type": "Cashless",'
            _lfeature_level=str(_ltmp_string[4])
            _lcountry_code=hex((_ltmp_string[5]*256)+_ltmp_string[6])
            _lscaling_factor=str(_ltmp_string[7])
            _ldecimal_places=str(_ltmp_string[8])
            _lcan_revalue=_ltmp_string[9] & 0b00000001
            if _lcan_revalue == 0x01:
                _lcan_revalue_string = "True"
            else:
                _lcan_revalue_string = "False"            
            _lmanufacturer=_ltmp_string[12:15].decode()
            _lserial_number=_ltmp_string[15:27].decode()
            _lserial_model=_ltmp_string[27:39].decode()
            _lsoftware_version=str((_ltmp_string[40]*256)+_ltmp_string[41])
            
            _ljson_string+='"level": "'+_lfeature_level+'",'
            _ljson_string+='"CurrencyCode": "'+_lcountry_code[2:]+'",'
            _ljson_string+='"ScalingFactor": "'+_lscaling_factor+'",'
            _ljson_string+='"DecimalPlaces": "'+_ldecimal_places+'",'
            _ljson_string+='"CanRevalue": "'+_lcan_revalue_string+'",'
            _ljson_string+='"Manufacturer": "'+_lmanufacturer+'",'
            _ljson_string+='"SerialNumber": "'+_lserial_number+'",'
            _ljson_string+='"Model": "'+_lserial_model+'",'
            _ljson_string+='"SWVersion": "'+_lsoftware_version+'"'
            _ljson_string+='}\n'
            _lsock.send(_ljson_string.encode())
            return True
        else:
            return False
    else:
        return False


# server parse and execute received message
def server_prel_messages(_lser,_lsock,_llsir):
    try:
        _lsir=_llsir.decode()
    except:
        print("Malformated command")
        return
    _lsir=_lsir.upper()
    # daca e MDBBILLinit
    if _lsir.find("MDBBILLINIT")!=-1:
        print("Trying to INIT bill validator... ")
        if mdb_bill_init(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBBILLENABLE")!=-1:
        print("Trying to ENABLE bill validator... ")
        if mdb_bill_enable(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")        
    elif _lsir.find("MDBBILLDISABLE")!=-1:
        print("Trying to DISABLE bill validator... ")
        if mdb_bill_disable(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")        
    elif _lsir.find("MDBBILLSETTINGS")!=-1:
        print("Trying to get INTERNAL SETTINGS from bill validator... ")
        if mdb_bill_get_settings(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("MDBCOININIT")!=-1:
        print("Trying to INIT coin acceptor... ")
        if mdb_coin_init(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")        
    elif _lsir.find("MDBCOINENABLE")!=-1:
        print("Trying to ENABLE coin acceptor... ")
        if mdb_coin_enable(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCOINDISABLE")!=-1:
        print("Trying to DISABLE coin acceptor... ")
        if mdb_coin_disable(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")    
    elif _lsir.find("MDBCOINSETTINGS")!=-1:
        print("Trying to get INTERNAL SETTINGS from coin acceptor... ")
        if mdb_coin_get_settings(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")    
    elif _lsir.find("MDBSETMAXCREDIT(")!=-1:
        print("Receiving MAX CREDIT... ")
        _gmax_credit=mdb_set_max_credit(_lser,_lsock,_lsir)
    elif _lsir.find("MDBCREDITRESET")!=-1:
        print("Trying to RESET CURRENT CREDIT... ")
        if mdb_credit_reset(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBSETCHANGE(")!=-1:
        print("Trying to RETURN CHANGE... ")
        if mdb_set_change(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBSETCURRENTCREDIT(")!=-1:
        print("Trying to set CURRENT CREDIT... ")
        if mdb_set_current_credit(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBPOLL")!=-1:
        print("Trying to POLL MDB IFC... ")
        if mdb_poll(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBRESETSTATUS")!=-1:
        print("Trying to RESET PMS STATUSES... ")
        if mdb_reset_status(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSINIT(")!=-1:
        print("Trying to INIT cashless... ")
        if mdb_cashless_init(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSENABLE(")!=-1:
        print("Trying to ENABLE cashless... ")
        if mdb_cashless_enable(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSDISABLE(")!=-1:
        print("Trying to ENABLE cashless... ")
        if mdb_cashless_disable(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSVENDCANCEL(")!=-1:
        print("Trying to VEND CANCEL on cashless... ")
        if mdb_cashless_vend_cancel(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSVENDREQUEST(")!=-1:
        print("Trying to send VEND REQUEST to cashless... ")
        if mdb_cashless_vend_request(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSVENDSUCCESS(")!=-1:
        print("Trying to send VEND SUCCESS to cashless... ")
        if mdb_cashless_vend_success(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("MDBCASHLESSVENDFAILED(")!=-1:
        print("Trying to send VEND FAILED to cashless... ")
        if mdb_cashless_vend_failed(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSREVALUE(")!=-1:
        print("Trying to send REVALUE to cashless... ")
        if mdb_cashless_revalue(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSENDSESSION(")!=-1:
        print("Trying to send END SESSION to cashless... ")
        if mdb_cashless_end_session(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBCASHLESSSETTINGS(")!=-1:
        print("Trying to get CASHLESS SETTINGS... ")
        if mdb_cashless_get_settings(_lser,_lsock,_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BYE")!=-1:
        sys.exit(0)
    else:
       _lsock.send(json.dumps({"UnknownCommand" : "failed"}).encode()+b"\r\n")
        
 
# Main Procedure
def MainProcedure():
    host = "0.0.0.0"
    port = 5127
    if len(sys.argv)<2:
        print("You have to give me the serial port as a parameter :-)")
        sys.exit(1)
    print("Opening serial port")
    
    try:
        #_ser=serial.Serial(port=sys.argv[1],baudrate=57600,timeout=2,rtscts=True,xonxoff=False)
        _ser=serial.Serial(port=sys.argv[1],baudrate=115200,timeout=2,rtscts=True,xonxoff=False)
        if _ser.isOpen()==False:
            print("Cannot open serial port")
            sys.exit(2)
    except:
        print("Error opening serial port")
        sys.exit(3)
    try:
#        global sock
#        global conn
#        global addr
        conn = socket.socket()
        conn.bind((host,port))
        conn.listen(1)
        _sock, addr = conn.accept()
        time.sleep(1)
        _sock.send(json.dumps({"AppName" : "MDBMasterRS232IFC","Version" : "1.08","CreatedBy" : "www.vendingtools.ro"}).encode()+b"\n")
    except:
        print("Cannot open socket for listening. Maybe the port is in use.")
        sys.exit(4)

    while True:
        _gsir = _sock.recv(1024)
        if len(_gsir)>3:
           # parse and execute received command
           server_prel_messages(_ser,_sock,_gsir);
           pass
        else:
            # connection closed, wait for the next one
            conn.listen(1)
            _sock, addr = conn.accept()

    conn.close()
     
if __name__ == '__main__':
    MainProcedure()
