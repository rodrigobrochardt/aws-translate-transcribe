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

s3_client = boto3.client("s3",region_name="us-east-1",
                              aws_access_key_id="ASIAZ2PGSF5Q72L6WHWA",
                              aws_secret_access_key="1pdjOc4ye2JpCVRKlKB0KRI2lJh092xvNvwrDs/r",
                              aws_session_token="FwoGZXIvYXdzECUaDNAo3obzntbo++eNsiK4Ad8cpVgbtEzknlcpeHPPaV+OWGERKqRTjb0s8MFIn6gdZ1U50EuEyAWlrf8UqnRGxCLguUTpTD9PC80cekQuKY4uXlnrGfknJHqGoiPYw59gT4aqVfChqdNnVzu6Fi3iVKN4jG4rVWf6L3fSHtlCME6uu3UprDilGn5yQ7BM++fwrGdamqIWMagdWUt4CDN9QnKwXDNSbcvofwIXiSHKwpNPJrLNpBUFZc0y+YiYNNBBXfBP8bL26ncosM+UjQYyLW4mvNI6Nl8T7I1Ha828prA5wleoRMMCP2XYSaWF+NkPvtX6Y4goRFtX1KCxwg==")
transcribe_client = boto3.client("transcribe",region_name="us-east-1",
                                              aws_access_key_id="ASIAZ2PGSF5Q72L6WHWA",
                              aws_secret_access_key="1pdjOc4ye2JpCVRKlKB0KRI2lJh092xvNvwrDs/r",
                              aws_session_token="FwoGZXIvYXdzECUaDNAo3obzntbo++eNsiK4Ad8cpVgbtEzknlcpeHPPaV+OWGERKqRTjb0s8MFIn6gdZ1U50EuEyAWlrf8UqnRGxCLguUTpTD9PC80cekQuKY4uXlnrGfknJHqGoiPYw59gT4aqVfChqdNnVzu6Fi3iVKN4jG4rVWf6L3fSHtlCME6uu3UprDilGn5yQ7BM++fwrGdamqIWMagdWUt4CDN9QnKwXDNSbcvofwIXiSHKwpNPJrLNpBUFZc0y+YiYNNBBXfBP8bL26ncosM+UjQYyLW4mvNI6Nl8T7I1Ha828prA5wleoRMMCP2XYSaWF+NkPvtX6Y4goRFtX1KCxwg==")
translate_client = boto3.client("translate",
                                              region_name="us-east-1",
                                              aws_access_key_id="ASIAZ2PGSF5Q72L6WHWA",
                              aws_secret_access_key="1pdjOc4ye2JpCVRKlKB0KRI2lJh092xvNvwrDs/r",
                              aws_session_token="FwoGZXIvYXdzECUaDNAo3obzntbo++eNsiK4Ad8cpVgbtEzknlcpeHPPaV+OWGERKqRTjb0s8MFIn6gdZ1U50EuEyAWlrf8UqnRGxCLguUTpTD9PC80cekQuKY4uXlnrGfknJHqGoiPYw59gT4aqVfChqdNnVzu6Fi3iVKN4jG4rVWf6L3fSHtlCME6uu3UprDilGn5yQ7BM++fwrGdamqIWMagdWUt4CDN9QnKwXDNSbcvofwIXiSHKwpNPJrLNpBUFZc0y+YiYNNBBXfBP8bL26ncosM+UjQYyLW4mvNI6Nl8T7I1Ha828prA5wleoRMMCP2XYSaWF+NkPvtX6Y4goRFtX1KCxwg==")
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
  print(text)
  textTranslated = translate_client.translate_text(Text=text,SourceLanguageCode="auto",TargetLanguageCode="en")["TranslatedText"]
  return flask.redirect("http://127.0.0.1:5500/?translated={}".format(textTranslated))
app.run()