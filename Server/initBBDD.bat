mysql -u root -p < .\BBDD\BBDD_create_tables.sql
cd PythonServer
python.exe .\loadData.py
pause