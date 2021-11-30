from os import terminal_size
import boto3
import botocore
import flask
from flask import request
from flask_cors import CORS,cross_origin
import json
import urllib

app = flask.Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config["CORS_HEADERS"] = 'Content-Type'

aws_access_key_id="ASIAZ2PGSF5Q5MGTWRS5"
aws_secret_access_key="t0hXvZldSzzlDBmUVqclArn7WxurokRUzMP/R5ES"
aws_session_token="FwoGZXIvYXdzEDYaDD7qiMDBUym80nxITiK4AUPCZE0rOzvwSHzQBZns1PG2C37gSeldaL62FAbuRm1SRG6drfhca8XbwaaMrcrT1CzBJuvpnCM7u7oz5eYqC/sX8azuudM2fx9wL1VlWKup0GRMKYXIk5jhEarcEwNTojMM1EF9vBZVbzx1/33pXiWZeR/GFs7V23CyuD1o266A512u8DFfEFic5xyv82EOELt6fzWOPb+kbykFmNP7SJqtB09QOZZJpkw36GgbCtYCn3Yn9PgFGL8oycGYjQYyLSGojvRCfacODWajERJrOUu/49n6fA3jk0oQNPEf5yeLS1gZn75UUO2dDRqA9A=="

s3_client = boto3.client("s3",region_name="us-east-1",
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
transcribe_client = boto3.client("transcribe",region_name="us-east-1",
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
translate_client = boto3.client("translate",region_name="us-east-1",
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
def isFileExists():
  try:
    s3_client.get_object(Bucket='bucket-projeto-pisi4', Key='audio.mp3')
    return True
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        return False

def isBucketExists():
  try:
    s3_client.head_bucket(Bucket='bucket-projeto-pisi4')
    return True
  except botocore.exceptions.ClientError as e:  
    error_code = e.response['Error']['Code']
    if error_code == '404':
        return False



@app.route('/transcribe', methods=['POST'])
@cross_origin()
def transcribe():
  if isBucketExists() is not True:
    s3_client.create_bucket(Bucket='bucket-projeto-pisi4')
  if isFileExists():
    s3_client.delete_object(Bucket='bucket-projeto-pisi4', Key='audio.mp3')
  s3_client.put_object(Bucket="bucket-projeto-pisi4", Key="audio.mp3",Body=request.files["myfile"])

  transcribe_client.start_transcription_job(TranscriptionJobName="transcription_audio",
                                            Media={'MediaFileUri':'s3://bucket-projeto-pisi4/audio.mp3'},
                                            MediaFormat='mp3',
                                            LanguageCode='pt-BR')
  tries = 0
  while tries < 50:
    tries+=1
    job = transcribe_client.get_transcription_job(TranscriptionJobName="transcription_audio")
    jobStatus = job['TranscriptionJob','TranscriptionJobStatus']
    if jobStatus == 'COMPLETED':
      response = urllib.request.urlopen(job['TranscriptionJob']["Transcript"]["TranscriptFileUri"])
      data = json.loads(response.read())
      text = data['results']['transcripts'][0]['transcript']
      break

  return flask.redirect("http://127.0.0.1:5500/?transcribed={}".format(text))


@app.route('/translate', methods=['POST'])
@cross_origin()
def translate():
  text = request.data.decode()[6:].rstrip()
  textTranslated = translate_client.translate_text(Text=text,SourceLanguageCode="auto",TargetLanguageCode="en")["TranslatedText"]
  return flask.redirect("http://127.0.0.1:5500/?translated={}".format(textTranslated))
app.run()