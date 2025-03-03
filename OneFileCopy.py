## Create a new Document in Google Drive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
folder = "1rXMhpHPMwDl9vOAdjdBoDO-i9ENz6cXH"
title = "Copy of my other file"
file = "1NRPnllb78cHahdypcn8tqc_-V08shLgwRQtYmnfk5jQ"
drive.auth.service.files().copy(fileId=file,
                           body={"parents": [{"kind": "drive#fileLink",
                                 "id": folder}], 'title': title}).execute()