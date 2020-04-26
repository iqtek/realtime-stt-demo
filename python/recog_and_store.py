#! /usr/bin/env python3
import logging
from audio import audio_open_read
from tinkoff.cloud.stt.v1 import stt_pb2_grpc, stt_pb2
from auth import authorization_metadata
from common import build_first_streaming_recognition_request, make_channel, \
        print_streaming_recognition_responses, StreamingRecognitionParser
from icecream import ic
from asterisk.agi import *
import settings as cfg
import os
import binascii
import pymysql.cursors
import cent
import time
import uuid

logger = logging.getLogger()
AUDIO_FD = 3

dbcon = pymysql.connect(host=cfg.mysql_host,
    user=cfg.mysql_user,
    password=cfg.mysql_password,
    db=cfg.mysql_db)

client = cent.Client(cfg.centrifugo_api, timeout=1)
cent_channel = "calls"

def generate_requests(args, agi):
    try:
        yield build_first_streaming_recognition_request(args)
        i=0
        while True:
            i = i + 1
            if agi != None:
                data = os.read(AUDIO_FD, 8000)
            else:
                data = bytes(160)
            if i == 1: # drop initial data
                continue
            #if agi != None:
            #    agi.verbose("Frame: %d(%d): %s" % (i, len(data), binascii.hexlify(data)))
            #else:
            #    print("Frame: %d(%d): %s" % (i, len(data), binascii.hexlify(data)))
            if not data:
                break
            request = stt_pb2.StreamingRecognizeRequest()
            request.audio_content = data
            if agi == None and i>20:
                sys.exit()
            yield request
    except:
        logger.exception("Got exception in generate_requests")
        raise

def save_streaming_recognition_responses(responses, agi, ani, uid, call_id):
    for response in responses:
        for result in response.results:
            if agi != None:
                agi.verbose("Is Final: %s" % str(result.is_final))
            else:
                print("Is Final: %s" % str(result.is_final))

            for alternative in result.recognition_result.alternatives:
                if agi != None:
                    agi.verbose("Transcription: %s" % str(alternative.transcript))
                    agi.verbose("Confidence: %s" % str(alternative.confidence))
                else: 
                    print("Transcription: %s" % str(alternative.transcript))
                    print("Confidence: %s" % str(alternative.confidence))

                try:
                    with dbcon.cursor() as cursor:
                        sql = "SELECT id FROM phrases WHERE uniqueid=%s AND ISNULL(final)"
                        cursor.execute(sql, (uid))
                        
                        data = {"type": "phrase", 
                            "uniqueid": uid, 
                            "phrase": str(alternative.transcript), 
                            "call_id": call_id, 
                            "final": False}
                        if cursor.rowcount == 0:
                            sql = "INSERT INTO phrases SET phrase=%s,date=NOW(),uniqueid=%s"
                            cursor.execute(sql, (str(alternative.transcript),uid))
                            data["phrase_id"] = cursor.lastrowid
                        elif result.is_final:
                            pid = cursor.fetchone()
                            sql = "UPDATE phrases SET phrase=%s,date=NOW(),final=1 WHERE uniqueid=%s AND ISNULL(final)"
                            cursor.execute(sql, (str(alternative.transcript),uid))
                            data["final"] = True
                            data["phrase_id"] = pid[0]
                        else:
                            pid = cursor.fetchone()
                            sql = "UPDATE phrases SET phrase=%s,date=NOW() WHERE uniqueid=%s AND ISNULL(final)"
                            cursor.execute(sql, (str(alternative.transcript),uid))
                            data["phrase_id"] = pid[0]
                finally:
                    dbcon.commit()
                client.publish(cent_channel, data)
                if agi == None:
                    ic(data)
                break
            if agi != None:
                agi.verbose("------------------")
            else:
                print("------------------")
            

def main():
    agi = AGI()
    #agi = None
    if agi != None:
        agi.verbose("EAGI script started...")
        ani = agi.env['agi_callerid']
        uid = agi.env['agi_uniqueid']
        agi.verbose("Call answered from: %s with id %s" % (ani, uid))
    else:
        ani = ""
        uid = str(uuid.uuid4())

    try:
        with dbcon.cursor() as cursor:
            sql = "INSERT INTO calls SET uniqueid=%s,callerid=%s,calldate=NOW()";
            cursor.execute(sql, (uid, ani))
            call_id = cursor.lastrowid
    finally:
        dbcon.commit()

    data = {"type": "call", 
        "unqueid": uid,
        "callerid": ani[-4:], 
        "calldate": time.strftime('%Y-%m-%d %H:%M:%S'), 
        "call_id": call_id }
    client.publish(cent_channel, data)
    if agi == None:
        ic(data)
        
    
    args = StreamingRecognitionParser().parse_args()
    
    stub = stt_pb2_grpc.SpeechToTextStub(make_channel(args))
    metadata = authorization_metadata(cfg.api_key, cfg.secret_key, "tinkoff.cloud.stt")
    responses = stub.StreamingRecognize(generate_requests(args, agi), metadata=metadata)
    save_streaming_recognition_responses(responses, agi, ani, uid, call_id)

if __name__ == "__main__":
    main()
