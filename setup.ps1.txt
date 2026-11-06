
#Requires -Version 5.1
<#
.SYNOPSIS
    GamepadMouse + Hex AI Coding Workflow Installer

.DESCRIPTION
    - Installs Hex by Anomaly
    - Downloads the latest published GamepadMouse GitHub Release
    - Supports portable EXE, ZIP, and MSI assets
    - Creates shortcuts for portable builds
    - Optionally launches GamepadMouse on Windows startup

.EXAMPLE
    .\setup.ps1

.EXAMPLE
    .\setup.ps1 -StartWithWindows

.EXAMPLE
    .\setup.ps1 -AssetName "GamepadMouse.exe" -SkipHex
#>

[CmdletBinding()]
param(
    [string]$AssetName = "",
    [string]$ExeName = "",
    [string]$ExpectedSha256 = "",
    [switch]$SkipHex,
    [switch]$StartWithWindows
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$Repo = "ayazmirza54/gamepadmouse"
$HexInstallerUrl = "https://anoma.ly/hex/files/install-windows.ps1"

$InstallRoot = Join-Path $env:LOCALAPPDATA "Programs\GamepadMouse"
$TempDir = Join-Path $env:TEMP (
    "GamepadMouse-" + [guid]::NewGuid().ToString("N")
)

# Helpers
function Write-Step {
    param([string]$Message)
    Write-Host "`n[>] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function New-AppShortcut {
    param(
        [string]$Target,
        [string]$LinkPath
    )

    $Parent = Split-Path -Parent $LinkPath
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null

    $Shell = New-Object -ComObject WScript.Shell
    $Shortcut = $Shell.CreateShortcut($LinkPath)
    $Shortcut.TargetPath = $Target
    $Shortcut.WorkingDirectory = Split-Path -Parent $Target
    $Shortcut.IconLocation = "$Target,0"
    $Shortcut.Save()
}

function Get-AppExecutable {
    param([string]$Directory)

    $Files = @(
        Get-ChildItem -LiteralPath $Directory -Recurse -File -Filter "*.exe" |
        Where-Object {
            $_.Name -notmatch "^(unins|uninstall|updater|crashpad|vc_redist)"
        }
    )

    if ($ExeName) {
        $Matches = @($Files | Where-Object { $_.Name -eq $ExeName })
    }
    else {
        $Matches = @(
            $Files | Where-Object {
                $_.BaseName -match "(?i)gamepad.*mouse"
            }
        )

        if ($Matches.Count -eq 0 -and $Files.Count -eq 1) {
            $Matches = $Files
        }
    }

    if ($Matches.Count -ne 1) {
        $Names = ($Files | ForEach-Object { $_.FullName }) -join "`n"
        throw "Cannot uniquely identify the app executable. Use -ExeName.`n$Names"
    }

    return $Matches[0]
}

try {
    if (-not [Environment]::Is64BitOperatingSystem) {
        throw "This installer requires 64-bit Windows."
    }

    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Magenta
    Write-Host "       GAMEPAD CODING WORKFLOW" -ForegroundColor Magenta
    Write-Host "          Powered by Hex + AI" -ForegroundColor Magenta
    Write-Host "============================================" -ForegroundColor Magenta

    # STEP 1: Install Hex
    if (-not $SkipHex) {
        $HexCommand = Join-Path $env:APPDATA "hex\bin\hex.com"

        if (Test-Path -LiteralPath $HexCommand) {
            Write-Success "Hex already installed."
        }
        else {
            Write-Step "Downloading official Hex installer..."

            $HexScript = Join-Path $TempDir "install-hex.ps1"

            Invoke-WebRequest `
                -Uri $HexInstallerUrl `
                -OutFile $HexScript `
                -UseBasicParsing

            Write-Step "Installing Hex..."

            $HexProcess = Start-Process `
                -FilePath "powershell.exe" `
                -ArgumentList @(
                    "-NoProfile",
                    "-ExecutionPolicy", "Bypass",
                    "-File", "`"$HexScript`""
                ) `
                -Wait `
                -PassThru

            if ($HexProcess.ExitCode -ne 0) {
                throw "Hex installer returned exit code $($HexProcess.ExitCode)."
            }

            Write-Success "Hex installer completed."
        }
    }
    else {
        Write-Step "Skipping Hex installation."
    }

    # STEP 2: Locate latest GitHub Release
    Write-Step "Checking GamepadMouse releases..."

    $Headers = @{
        "User-Agent" = "GamepadMouse-Setup"
        "Accept"     = "application/vnd.github+json"
    }

    $ApiUrl = "https://api.github.com/repos/$Repo/releases?per_page=20"

    $Releases = @(
        Invoke-RestMethod -Uri $ApiUrl -Headers $Headers |
        Where-Object { -not $_.draft }
    )

    if ($Releases.Count -eq 0) {
        throw "No published GitHub Release found at https://github.com/$Repo/releases"
    }

    $Release = $Releases[0]

    Write-Success "Found release: $($Release.tag_name)"

    # STEP 3: Select downloadable asset
    $Candidates = @(
        $Release.assets | Where-Object {
            $_.name -match "\.(exe|zip|msi)$" -and
            $_.name -notmatch "(?i)(source|symbols|debug)"
        }
    )

    if ($AssetName) {
        $Selected = @(
            $Candidates | Where-Object { $_.name -eq $AssetName }
        )
    }
    else {
        $Named = @(
            $Candidates | Where-Object {
                $_.name -match "(?i)(gamepad|mouse)"
            }
        )

        if ($Named.Count -eq 1) {
            $Selected = $Named
        }
        elseif ($Candidates.Count -eq 1) {
            $Selected = $Candidates
        }
        else {
            $Selected = @()
        }
    }

    if ($Selected.Count -ne 1) {
        $Available = ($Candidates | ForEach-Object { $_.name }) -join ", "
        throw "Could not select a unique release asset. Use -AssetName. Available: $Available"
    }

    $Asset = $Selected[0]
    $DownloadPath = Join-Path $TempDir $Asset.name

    Write-Step "Downloading $($Asset.name)..."

    Invoke-WebRequest `
        -Uri $Asset.browser_download_url `
        -Headers $Headers `
        -OutFile $DownloadPath `
        -UseBasicParsing

    # STEP 4: Verify download
    Write-Step "Calculating SHA-256..."

    $Hash = (Get-FileHash -LiteralPath $DownloadPath -Algorithm SHA256).Hash

    Write-Host "SHA-256: $Hash"

    if ($ExpectedSha256) {
        if ($Hash -ine $ExpectedSha256.Trim()) {
            throw "SHA-256 mismatch. Installation stopped."
        }
        Write-Success "SHA-256 verified."
    }

    # STEP 5: Install GamepadMouse
    $SafeTag = $Release.tag_name -replace '[^\w.-]', '_'
    $InstallDir = Join-Path $InstallRoot $SafeTag

    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

    $Extension = [IO.Path]::GetExtension($Asset.name).ToLowerInvariant()
    $AppExe = $null

    Write-Step "Installing GamepadMouse..."

    switch ($Extension) {
        ".zip" {
            # ZIP is expected to contain a portable Windows build
            Expand-Archive `
                -LiteralPath $DownloadPath `
                -DestinationPath $InstallDir `
                -Force

            $AppExe = Get-AppExecutable -Directory $InstallDir
        }

        ".exe" {
            if ($Asset.name -match '(?i)(setup|installer|install)') {
                # Conventional installer: let it handle its own paths
                $Process = Start-Process `
                    -FilePath $DownloadPath `
                    -Wait `
                    -PassThru

                if ($Process.ExitCode -ne 0) {
                    throw "GamepadMouse installer exited with code $($Process.ExitCode)."
                }
            }
            else {
                # Portable standalone executable
                $Target = Join-Path $InstallDir $Asset.name
                Copy-Item -LiteralPath $DownloadPath -Destination $Target -Force
                $AppExe = Get-Item -LiteralPath $Target
            }
        }

        ".msi" {
            $Process = Start-Process `
                -FilePath "msiexec.exe" `
                -ArgumentList "/i `"$DownloadPath`"" `
                -Wait `
                -PassThru

            if ($Process.ExitCode -ne 0) {
                throw "MSI installation exited with code $($Process.ExitCode)."
            }
        }

        default {
            throw "Unsupported release asset: $Extension"
        }
    }

    Write-Success "GamepadMouse installation completed."

    # STEP 6: Shortcuts and startup
    if ($null -ne $AppExe) {
        $StartMenu = [Environment]::GetFolderPath("Programs")
        $ShortcutPath = Join-Path $StartMenu "GamepadMouse.lnk"

        New-AppShortcut `
            -Target $AppExe.FullName `
            -LinkPath $ShortcutPath

        Write-Success "Created Start Menu shortcut."

        if ($StartWithWindows) {
            $StartupDir = [Environment]::GetFolderPath("Startup")
            $StartupLink = Join-Path $StartupDir "GamepadMouse.lnk"

            New-AppShortcut `
                -Target $AppExe.FullName `
                -LinkPath $StartupLink

            Write-Success "Enabled launch at login."
        }

        # STEP 7: Launch
        Write-Step "Launching GamepadMouse..."

        Start-Process `
            -FilePath $AppExe.FullName `
            -WorkingDirectory $AppExe.DirectoryName
    }
    else {
        Write-Host "The conventional installer manages app shortcuts and startup." -ForegroundColor Yellow
    }

    # STEP 8: Configuration instructions
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "            SETUP COMPLETE" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green

    Write-Host ""
    Write-Host "CONTROLLER CONFIGURATION" -ForegroundColor Yellow
    Write-Host "1. Connect your EvoFox controller."
    Write-Host "2. Open GamepadMouse."
    Write-Host "3. Open Hex and complete its first-run model setup."
    Write-Host "4. Map your chosen controller button to Ctrl+Space."
    Write-Host "5. In Hex, use Tap/Toggle mode for press-to-start/stop."
    Write-Host "   Or use Hold mode for push-to-talk."
    Write-Host "6. Focus your AI coding agent's input field."
    Write-Host "7. Press the button, dictate, then submit your prompt."

    Write-Host ""
    Write-Host "GamepadMouse: https://github.com/$Repo"
    Write-Host "Hex: https://anoma.ly/hex/"
    Write-Host ""
    Write-Host "Happy coding. Game on!" -ForegroundColor Magenta
}
catch {
    Write-Host ""
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    if (Test-Path -LiteralPath $TempDir) {
        Remove-Item `
            -LiteralPath $TempDir `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue
    }
}
