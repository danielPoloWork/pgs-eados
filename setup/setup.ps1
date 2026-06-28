#Requires -Version 5.1
<#
.SYNOPSIS
  setup.ps1 - guided EADOS installer for Windows: the PowerShell-native equivalent of the POSIX
  setup.sh. It downloads the factory bundle (pgs-eados-bundle.tar.gz), VERIFIES its SHA256
  (fail-closed), and extracts it ADDITIVELY (refuses to overwrite any existing file) into a target
  repo root. It is interactive when run bare (double-click via setup.bat) and scriptable via
  parameters. Scope = bundle download + placement only (USAGE section 6's consumer step), not the
  agentic-OS init. The installer lives OUTSIDE .eados-core/ because it *delivers* it.

  It adds NO new install logic versus the POSIX script - same fail-closed integrity and additive
  no-clobber guarantee (the ADR-0007 principle). Uses tar.exe (Windows 10 1803+) for the .tar.gz,
  mirroring setup.sh. PowerShell 5.1 / 7 compatible; ASCII-only (5.1 reads no-BOM scripts as ANSI).
#>
[CmdletBinding()]
param(
  [ValidateSet('new', 'existing')] [string]$Mode = 'existing',
  [string]$Path = '.',
  [string]$RepoName = '',
  [string]$Ref = 'latest',
  [string]$Repo = 'danielPoloWork/pgs-eados',
  [string]$From = '',
  [string]$BundleUrl = '',
  [string]$Sha256 = '',
  [string]$SumsFile = '',
  [switch]$NoVerify,
  [switch]$NoGh,
  [switch]$PrintPlan,
  [switch]$DryRun,
  [switch]$Interactive,
  [switch]$NonInteractive,
  [switch]$Help
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$BundleName = 'pgs-eados-bundle.tar.gz'
$SumsName = 'SHA256SUMS'

# Output to the real stdout/stderr (not Write-Host) so it is captured identically on PS 5.1 and 7.
function Info([string]$m) { [Console]::Out.WriteLine($m) }
function Warn([string]$m) { [Console]::Error.WriteLine("setup.ps1: warning: $m") }
function Fail([int]$code, [string]$m) { [Console]::Error.WriteLine("setup.ps1: error: $m"); exit $code }
function Die([string]$m) { Fail 1 $m }       # user / safety error
function Offline([string]$m) { Fail 2 $m }   # environmental: offline / asset unavailable

function Ask([string]$promptText, [string]$default) {
  if ($default) { [Console]::Error.Write("$promptText [$default]: ") } else { [Console]::Error.Write("${promptText}: ") }
  $a = [Console]::In.ReadLine()
  if ($null -eq $a) { [Console]::Error.WriteLine(''); $a = '' }
  $a = $a.TrimEnd("`r", "`n")
  if ([string]::IsNullOrEmpty($a)) { return $default } else { return $a }
}

function Confirm([string]$promptText) {
  [Console]::Error.Write("$promptText [y/N]: ")
  $a = [Console]::In.ReadLine()
  if ($null -eq $a) { [Console]::Error.WriteLine(''); $a = '' }
  return ($a.Trim() -match '^(y|yes)$')
}

function Show-Usage {
  Info @'
setup.ps1 - download the EADOS factory bundle into a repo (Windows; download + placement only).

USAGE
  setup.ps1 [options]            # bare / double-click (via setup.bat) => interactive prompts

WHERE TO INSTALL
  -Mode new|existing   install into a new repo dir or an existing one   (default: existing)
  -Path DIR            target repo root (existing), or parent dir (new)  (default: .)
  -RepoName NAME       name of the new repo dir under -Path             (required for -Mode new)

WHICH BUNDLE
  -Ref REF             release tag to install, e.g. v2.2.0              (default: latest)
  -Repo OWNER/REPO     source GitHub repo                               (default: danielPoloWork/pgs-eados)
  -From FILE           install from a local bundle file (skip download; air-gapped / testing)
  -BundleUrl URL       download the bundle from this exact URL (overrides -Ref / -Repo)

INTEGRITY (fail-closed: refuses to extract an unverified bundle)
  -Sha256 HEX          expected SHA256 of the bundle (else read from the release SHA256SUMS)
  -SumsFile FILE       verify against a local SHA256SUMS file (skip the download; air-gapped)
  -NoVerify            skip checksum verification (loudly; not recommended)

OTHER
  -Interactive         force the prompts even when parameters are given
  -NonInteractive      never prompt (use parameters / defaults)
  -NoGh                do not offer to create a GitHub repo with gh (new-repo mode)
  -DryRun              prompt + show the plan, but do not download / write / git-init
  -PrintPlan           print the resolved plan and exit (no download, no writes)
  -Help                this help

The bundle is extracted ADDITIVELY: it refuses to overwrite any existing file.
'@
}

if ($Help) { Show-Usage; exit 0 }

# Interactive when run bare (double-click) or asked for; never when -NonInteractive / -PrintPlan.
$wantInteractive = $false
if (-not $NonInteractive -and -not $PrintPlan) {
  if ($Interactive -or $PSBoundParameters.Count -eq 0) { $wantInteractive = $true }
}

if ($wantInteractive) {
  Info 'EADOS guided installer (Windows) - downloads the factory bundle into a repo (no agent init).'
  Info ''
  $ans = Ask 'Install into a (1) new repo or (2) existing repo?' '2'
  switch -Regex ($ans) {
    '^(1|new|n)$'      { $Mode = 'new' }
    '^(2|existing|e)$' { $Mode = 'existing' }
    default            { Die 'please answer 1 (new) or 2 (existing)' }
  }
  if ($Mode -eq 'new') {
    $Path = Ask 'Parent directory for the new repo' '.'
    $RepoName = ''
    $tries = 0
    while (-not $RepoName) {
      $RepoName = Ask 'New repo name' ''
      if (-not $RepoName) {
        $tries++
        if ($tries -ge 5) { Die 'a repo name is required for a new repo' }
        Info '  (a name is required for a new repo)'
      }
    }
  }
  else {
    $Path = Ask 'Path to the existing repo' '.'
  }
}

if ($Mode -eq 'new' -and -not $RepoName) { Die '-Mode new requires -RepoName' }

# --- resolve the plan (pure) ----------------------------------------------
if ($Mode -eq 'new') { $Target = "$Path/$RepoName" } else { $Target = $Path }

if ($BundleUrl) { $BundleUri = $BundleUrl; $SumsUri = ''; $SourceDesc = $BundleUrl }
elseif ($From) { $BundleUri = ''; $SumsUri = ''; $SourceDesc = "(local file) $From" }
elseif ($Ref -eq 'latest') {
  $BundleUri = "https://github.com/$Repo/releases/latest/download/$BundleName"
  $SumsUri = "https://github.com/$Repo/releases/latest/download/$SumsName"
  $SourceDesc = $BundleUri
}
else {
  $BundleUri = "https://github.com/$Repo/releases/download/$Ref/$BundleName"
  $SumsUri = "https://github.com/$Repo/releases/download/$Ref/$SumsName"
  $SourceDesc = $BundleUri
}

if ($NoVerify) { $VerifyDesc = 'DISABLED (-NoVerify)' }
elseif ($Sha256) { $VerifyDesc = "pinned $Sha256" }
elseif ($SumsFile) { $VerifyDesc = "$SumsName file ($SumsFile)" }
elseif ($SumsUri) { $VerifyDesc = "$SumsName from the release" }
else { $VerifyDesc = 'REQUIRED but no source (pass -Sha256, -SumsFile, or -NoVerify)' }

function Write-Plan {
  Info 'install plan:'
  Info "  mode:       $Mode"
  Info "  target:     $Target"
  Info "  source:     $SourceDesc"
  if (-not $From -and -not $BundleUrl) { Info "  repo:       $Repo"; Info "  ref:        $Ref" }
  Info "  checksum:   $VerifyDesc"
  Info '  extract:    additive (refuses to overwrite an existing file)'
}

if ($PrintPlan) { Write-Plan; exit 0 }

if ($wantInteractive) {
  Info ''; Info 'Plan:'; Write-Plan
  if ($Mode -eq 'new') { Info "  git init:   $Target (a fresh repository)" }
  Info ''
  if (-not (Confirm 'Proceed?')) { Info 'Aborted - nothing was written.'; exit 0 }
}

if ($DryRun) {
  Info "[dry-run] would install into $Target (mode $Mode)"
  if ($Mode -eq 'new') { Info "[dry-run] would git init: $Target" }
  exit 0
}

# --- run -------------------------------------------------------------------
# Resolve the target on disk.
if ($Mode -eq 'new') {
  if ((Test-Path -LiteralPath $Target) -and (Get-ChildItem -LiteralPath $Target -Force -ErrorAction SilentlyContinue | Select-Object -First 1)) {
    Die "target already exists and is not empty: $Target (use -Mode existing to add to it)"
  }
  New-Item -ItemType Directory -Force -Path $Target | Out-Null
}
else {
  if (-not (Test-Path -LiteralPath $Target -PathType Container)) {
    Die "target repo dir does not exist: $Target (create it, or use -Mode new)"
  }
}

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('eados-install-' + [System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
try {
  # Obtain the bundle.
  if ($From) {
    if (-not (Test-Path -LiteralPath $From -PathType Leaf)) { Die "bundle file not found: $From" }
    $bundle = $From
  }
  else {
    $bundle = Join-Path $tmp $BundleName
    Info "downloading $SourceDesc"
    try { Invoke-WebRequest -Uri $BundleUri -OutFile $bundle -UseBasicParsing }
    catch { Offline "download failed: $BundleUri (offline? wrong -Ref / -Repo?)" }
  }

  # It must be a readable gzip tarball; capture the listing for the safety checks.
  $listing = & tar -tzf $bundle 2>$null
  if ($LASTEXITCODE -ne 0) { Die "not a readable .tar.gz bundle: $bundle" }

  # Verify integrity (fail-closed).
  if ($NoVerify) {
    Warn "checksum verification DISABLED (-NoVerify) - the bundle's provenance is NOT checked"
  }
  else {
    $expected = $Sha256
    if (-not $expected) {
      # $SumsFile (the param) vs $sumsSrc (the resolved path) - PowerShell vars are case-insensitive,
      # so the local must NOT be named $sumsFile or it would clobber the parameter.
      if ($SumsFile) {
        if (-not (Test-Path -LiteralPath $SumsFile -PathType Leaf)) { Die "$SumsName file not found: $SumsFile" }
        $sumsSrc = $SumsFile
      }
      elseif ($SumsUri) {
        $sumsSrc = Join-Path $tmp $SumsName
        try { Invoke-WebRequest -Uri $SumsUri -OutFile $sumsSrc -UseBasicParsing }
        catch { Offline "could not fetch $SumsName ($SumsUri); pass -Sha256, -SumsFile, or -NoVerify" }
      }
      else { Die "cannot verify integrity (no $SumsName source for -From / -BundleUrl); pass -Sha256, -SumsFile, or -NoVerify" }
      foreach ($line in Get-Content -LiteralPath $sumsSrc) {
        $fields = $line -split '\s+'
        if ($fields.Count -ge 2) {
          $name = $fields[1] -replace '^\*', '' -replace '^\./', ''
          if ($name -eq $BundleName) { $expected = $fields[0]; break }
        }
      }
      if (-not $expected) { Die "$SumsName ($sumsSrc) has no entry for $BundleName; pass -Sha256 or -NoVerify" }
    }
    $actual = (Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $expected.ToLower()) { Die "checksum mismatch: expected $expected, got $actual" }
    Info "checksum OK ($actual)"
  }

  # Defense in depth: refuse an archive whose paths escape the target root.
  $unsafe = $listing | Where-Object { $_ -match '^/' -or $_ -match '(^|/)\.\.(/|$)' }
  if ($unsafe) { Die ("refusing to extract - the archive has unsafe paths:`n" + ($unsafe -join "`n")) }

  # Additive: refuse to overwrite any existing FILE (directories may coexist).
  $clobber = @()
  foreach ($entry in $listing) {
    if ($entry.EndsWith('/')) { continue }
    $dest = "$Target/$entry"
    if ((Test-Path -LiteralPath $dest) -and -not (Test-Path -LiteralPath $dest -PathType Container)) { $clobber += $entry }
  }
  if ($clobber.Count -gt 0) { Die ("refusing to overwrite existing files under $Target (install is additive):`n  " + ($clobber -join "`n  ")) }

  # Place it.
  & tar -xzf $bundle -C $Target
  if ($LASTEXITCODE -ne 0) { Die 'extraction failed' }
}
finally {
  Remove-Item -Recurse -Force -LiteralPath $tmp -ErrorAction SilentlyContinue
}

# git init for a new repo (the lifecycle 9.1 deferred).
if ($Mode -eq 'new') {
  if (Get-Command git -ErrorAction SilentlyContinue) {
    Push-Location $Target
    try { & git init -q; Info "git: initialised an empty repository in $Target" }
    catch { Info "note: 'git init' did not complete for $Target - you can run it yourself" }
    finally { Pop-Location }
  }
  else {
    Info "note: git not found - skipped 'git init' for $Target (install git, then run it there)"
  }
  if (-not $NoGh -and (Get-Command gh -ErrorAction SilentlyContinue)) {
    if (Confirm 'Create a GitHub repo for it now with gh?') {
      Push-Location $Target
      try { & gh repo create $RepoName --private --source=. --remote=origin }
      catch { Info "note: 'gh repo create' did not complete - you can run it later" }
      finally { Pop-Location }
    }
  }
}

Info ''
Info 'Done. Next:'
Info "  cd `"$Target`""
Info '  open the repo with an AI agent (it auto-loads AGENTS.md), or render deterministically:'
Info '  python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place'
