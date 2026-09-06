# AD CS configuration on CA01 — console output (RECALLED, not Captured)

Source: screenshot of CA01's noVNC console, 2026-09-05 approximately 22:08 UTC (console clock
reads 3:08 PM local, America/Los_Angeles).
Host: CA01 (VM 107), Administrator: Windows PowerShell
Status: **Recalled.** A screenshot is a file and it is still Recalled. The same facts are
re-read through the guest agent in evidence/12; cite that file, not this one, for any claim.

Command run at the console:

    Install-AdcsCertificationAuthority -CAType EnterpriseSubordinateCA -CACommonName "district.local Issuing CA" -KeyLength 4096 -HashAlgorithmName SHA256 -CryptoProviderName "RSA#Microsoft Software Key Storage Provider" -OutputCertRequestFile "C:\ca01.req" -Credential (Get-Credential) -Force

First attempt, transcribed from the screenshot:

    cmdlet Get-Credential at command pipeline position 1
    Supply values for the following parameters:
    Credential
    Get-Credential : Cannot process command because of one or more missing mandatory parameters: Credential.
    At line:1 char:268
    + ... tputCertRequestFile "C:\ca01.req" -Credential (Get-Credential) -Force
    + CategoryInfo          : InvalidArgument: (:) [Get-Credential], ParameterBindingException
    + FullyQualifiedErrorId : MissingMandatoryParameter,Microsoft.PowerShell.Commands.GetCredentialCommand

Second attempt, transcribed from the screenshot:

    cmdlet Get-Credential at command pipeline position 1
    Supply values for the following parameters:
    Credential
    WARNING: The Active Directory Certificate Services installation is incomplete. To complete the installation, use the
    request file "C:\ca01.req" to obtain a certificate from the parent CA. Then, use the Certification Authority snap-in to
    install the certificate. To complete this procedure, right-click the node with the name of the CA, and then click
    Install CA Certificate. The operation completed successfully. 0x0 (WIN32: 0)

    ErrorId ErrorString
    ------- -----------
        398 The Active Directory Certificate Services installation is incomplete. To complete the installation, use the ...
