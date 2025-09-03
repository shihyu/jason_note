#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 8/11/2018

# import os
# # 導入os庫,用於文件、路徑相關的解析

# def getPath(basePath, fileName):
#     extName = os.path.splitext(fileName)[1]
#     filePath = basePath
#     if(extName.lower() == ".txt"):
#         filePath += "/txt/"
#     elif(extName.lower() == ".pdf"):
#         filePath += "/pdf/"
#     else:
#         filePath += "/other/"
#
#     # 如果目錄不存在，則創建新目錄
#     if (not os.path.exists(filePath)):
#         os.makedirs(filePath)
#
#     filePath += fileName
#     return filePath


import os
# 導入os庫,用於文件、路徑相關的解析

def getPath(basePath, fileName):
    extName = fileName.split(".")[1]
    filePath = basePath + "/" + extName + "/"

    # 如果目錄不存在，則創建新目錄
    if (not os.path.exists(filePath)):
        os.makedirs(filePath)

    filePath += fileName
    return filePath

print(getPath("E:/upload", "TestFile.rar"))
print(getPath("E:/upload", "Design Pattern for Python.pdf"))