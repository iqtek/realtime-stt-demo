# -realtime-stt-demo
Realtime speech recognition demo application

Based on TCS speechkit examples: https://github.com/TinkoffCreditSystems/voicekit-examples

Based on EAGI vosk examples idea: https://github.com/alphacep/vosk-server/tree/master/client-samples/asterisk


To run with SSL:
./centrifugo --client_insecure --api_insecure -p 8443 --tls --tls_cert /etc/asterisk/keys/integration/certificate.pem --tls_key /etc/asterisk/keys/integration/webserver.key

Without SSL:
./centrifugo --client_insecure --api_insecure -p 8000

Please ask questions on Telagram channel: https://t.me/iqtek_qa