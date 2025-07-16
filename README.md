COLECCION DE POSTMAN: 
https://utecdevelopers.postman.co/workspace/Rides_IS~682b2c7d-2d3b-4fd8-b080-fcf876961504/collection/33936871-c9dd315b-1c01-4796-8ce2-540f3bb442bf?action=share&creator=33936871

Para usar la coleccion de Postman se tienen que ejecutar los examples dentro de cada request que necesite un body o un param, caso contrario ejecutar el mismo endpoint.


Para el unit test ejecutar
1. pytest tests/unittest.py -v
2. python3 -m coverage run -m pytest tests/unittest.py
3. python3 -m coverage report

