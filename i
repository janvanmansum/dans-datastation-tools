== Info:   Trying 127.0.0.1:20330...
== Info: Connected to localhost (127.0.0.1) port 20330 (#0)
=> Send header, 195 bytes (0xc3)
0000: POST /validate HTTP/1.1
0019: Host: localhost:20330
0030: User-Agent: curl/7.79.1
0049: Accept: */*
0056: Content-Length: 438
006b: Content-Type: multipart/form-data; boundary=--------------------
00ab: ----87a716c3e52c8a26
00c1: 
=> Send data, 438 bytes (0x1b6)
0000: --------------------------87a716c3e52c8a26
002c: Content-Disposition: form-data; name="command"; filename="comman
006c: d.json"
0075: Content-Type: application/json
0095: 
0097: {.  "bagLocation": "/Users/janm/git/service/data-station/dd-inge
00d7: st-flow/data/migration/out/test1/processed/0db66941-fa4d-4eee-96
0117: 8a-9f6e847de302/097f32eb-8105-4ee6-8616-64f78f76a849",.  "packag
0157: eType": "MIGRATION",.  "level": "STAND-ALONE".}
0188: --------------------------87a716c3e52c8a26--
== Info: We are completely uploaded and fine
== Info: Mark bundle as not supporting multiuse
<= Recv header, 17 bytes (0x11)
0000: HTTP/1.1 200 OK
<= Recv header, 37 bytes (0x25)
0000: Date: Thu, 22 Sep 2022 11:16:06 GMT
<= Recv header, 32 bytes (0x20)
0000: Content-Type: application/json
<= Recv header, 21 bytes (0x15)
0000: Content-Length: 353
<= Recv header, 2 bytes (0x2)
0000: 
<= Recv data, 353 bytes (0x161)
0000: {"Bag location":"/Users/janm/git/service/data-station/dd-ingest-
0040: flow/data/migration/out/test1/processed/0db66941-fa4d-4eee-968a-
0080: 9f6e847de302/097f32eb-8105-4ee6-8616-64f78f76a849","Name":"097f3
00c0: 2eb-8105-4ee6-8616-64f78f76a849","Profile version":"1.0.0","Info
0100: rmation package type":"MIGRATION","Level":"STAND-ALONE","Is comp
0140: liant":true,"Rule violations":[]}
== Info: Connection #0 to host localhost left intact
