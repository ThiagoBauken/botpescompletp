' ============================================
' 🎣 Fishing MageBOT v5.0 - Launcher Silencioso
' ============================================
' Inicia o bot SEM mostrar janela CMD
' ============================================

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Caminho do executável compilado
exePath = "dist\FishingMageBOT\FishingMageBOT.exe"

' Caminho alternativo se estiver na pasta dist
exePathAlt = "FishingMageBOT.exe"

' Verificar se existe e executar
If fso.FileExists(exePath) Then
    ' Executar .exe sem janela (0 = escondido, False = não esperar)
    WshShell.Run Chr(34) & exePath & Chr(34), 0, False
ElseIf fso.FileExists(exePathAlt) Then
    ' Executar alternativo
    WshShell.Run Chr(34) & exePathAlt & Chr(34), 0, False
Else
    ' Fallback: executar Python com pythonw (sem console)
    If fso.FileExists("main.py") Then
        WshShell.Run "pythonw.exe main.py", 0, False
    Else
        MsgBox "❌ Erro: Executável não encontrado!" & vbCrLf & vbCrLf & "Procurado em:" & vbCrLf & exePath & vbCrLf & exePathAlt, 16, "Fishing MageBOT"
    End If
End If

Set WshShell = Nothing
Set fso = Nothing
