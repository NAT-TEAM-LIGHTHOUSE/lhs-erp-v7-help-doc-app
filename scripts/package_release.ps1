<#
  Builds the deployment package for one environment.

    powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1 -Env uat
    powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1 -Env prod

  Result:  dist\lhs-erp-v7-help-doc-app_<version>_<env>.zip   (code only: no PDFs, no html\, no docs\)
  The zip contains the folder  LHS_ERP_HELP_DOC_V7\  - unzip it OVER the Tomcat webapp folder.
  It never contains docs\, html\ or menu\ , so your published documents are not touched.
#>
param(
    [Parameter(Mandatory = $true)][ValidateSet('uat', 'prod')][string]$Env,
    [switch]$SkipChecks
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not $SkipChecks) {
    python scripts\check.py
    if ($LASTEXITCODE -ne 0) { throw 'scripts\check.py reported problems - fix them (or use -SkipChecks).' }
}

$ver   = (Get-Content VERSION -Raw).Trim()
$stage = Join-Path $root ("dist\_stage_" + $Env)
$app   = Join-Path $stage 'LHS_ERP_HELP_DOC_V7'
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force $app | Out-Null

# code only - generated / content folders are excluded on purpose
$items = 'layout.html', 'index.html', 'README.txt', 'css', 'js', 'images', 'vendor', 'WEB-INF', 'config', 'guide', 'tools'
foreach ($i in $items) { Copy-Item (Join-Path 'webapp' $i) $app -Recurse -Force }
Get-ChildItem $app -Recurse -Include '__pycache__', '*.pyc', 'auto_update.log' -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# environment settings
Copy-Item ("deploy\env\{0}.app.properties" -f $Env) (Join-Path $app 'config\app.properties') -Force
Set-Content (Join-Path $app 'VERSION.txt') ("lhs-erp-v7-help-doc-app $ver ($Env) built " + (Get-Date -Format 'yyyy-MM-dd HH:mm'))

New-Item -ItemType Directory -Force dist | Out-Null
$zip = "dist\lhs-erp-v7-help-doc-app_{0}_{1}.zip" -f $ver, $Env
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $app -DestinationPath $zip
Remove-Item $stage -Recurse -Force
Write-Host ''
Write-Host "Package ready: $zip" -ForegroundColor Green
Write-Host 'Next: see docs\DEPLOYMENT.md  (unzip over webapps\ , then Ctrl+F5).'
