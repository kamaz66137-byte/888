param(
  [string]$Scope = "src"
)

$ErrorActionPreference = "Stop"

function Write-Utf8NoBom {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Content
  )
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function ConvertTo-RepoRelativePath {
  param([Parameter(Mandatory = $true)][string]$Path)
  $prefix = $repoRoot.TrimEnd('\') + '\'
  $escaped = '^' + [System.Text.RegularExpressions.Regex]::Escape($prefix)
  $relative = [System.Text.RegularExpressions.Regex]::Replace(
    $Path,
    $escaped,
    '',
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
  )
  return $relative.Replace('\', '/')
}

function Get-Sha1Hex {
  param([Parameter(Mandatory = $true)][string]$Text)
  $sha1 = [System.Security.Cryptography.SHA1]::Create()
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha1.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace('-', '').ToLowerInvariant()
  }
  finally {
    $sha1.Dispose()
  }
}

function Get-SemanticTokenList {
  param([Parameter(Mandatory = $true)][string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) {
    return @()
  }
  $normalized = $Text.ToLowerInvariant().Replace('\\', '/').Replace('_', ' ').Replace('-', ' ')
  return [System.Text.RegularExpressions.Regex]::Split($normalized, '[^\p{L}\p{Nd}]+') |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and $_.Length -ge 2 }
}

function ConvertTo-TokenWeightMap {
  param([Parameter(Mandatory = $true)][string[]]$Tokens)
  $weights = @{}
  foreach ($token in $Tokens) {
    if ($weights.ContainsKey($token)) {
      $weights[$token] += 1.0
    }
    else {
      $weights[$token] = 1.0
    }
  }
  return $weights
}

function ConvertTo-HashedSparseVector {
  param(
    [Parameter(Mandatory = $true)][hashtable]$TokenWeightMap,
    [int]$Dimensions = 256
  )

  $buckets = @{}
  foreach ($token in $TokenWeightMap.Keys) {
    $tokenHashHex = (Get-Sha1Hex -Text $token).Substring(0, 8)
    $idx = [Convert]::ToInt32($tokenHashHex, 16) % $Dimensions
    if ($buckets.ContainsKey($idx)) {
      $buckets[$idx] += [double]$TokenWeightMap[$token]
    }
    else {
      $buckets[$idx] = [double]$TokenWeightMap[$token]
    }
  }

  $sumSquares = 0.0
  foreach ($value in $buckets.Values) {
    $sumSquares += ($value * $value)
  }
  $norm = [Math]::Sqrt($sumSquares)
  if ($norm -le 0) {
    $norm = 1.0
  }

  $indices = @($buckets.Keys | Sort-Object)
  $values = @()
  foreach ($idx in $indices) {
    $values += [Math]::Round(($buckets[$idx] / $norm), 6)
  }

  return [ordered]@{
    dim = $Dimensions
    indices = $indices
    values = $values
  }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path

$effectiveScope = "src"
if ($Scope -ne "src" -and $Scope -ne ".\src") {
  Write-Host "INFO: force scope to src/ (requested: $Scope)"
}

$scopePath = Join-Path $repoRoot $effectiveScope
if (-not (Test-Path $scopePath)) {
  throw "Scope path not found: $scopePath"
}

$outRoot = Join-Path $repoRoot "artifacts/code-map"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $outRoot ("history/" + $timestamp)
$latestDir = Join-Path $outRoot "latest"

New-Item -ItemType Directory -Force -Path $runDir | Out-Null
New-Item -ItemType Directory -Force -Path $latestDir | Out-Null

$structureFile = Join-Path $runDir "structure-map.txt"
$statsFile = Join-Path $runDir "language-stats.txt"
$pyImportsFile = Join-Path $runDir "imports-python.txt"
$tsjsImportsFile = Join-Path $runDir "imports-tsjs.txt"
$contextFile = Join-Path $runDir "context-cards.md"
$impactFile = Join-Path $runDir "impact-analysis.md"
$trackFile = Join-Path $runDir "change-tracking.md"
$manifestFile = Join-Path $runDir "manifest.json"
$semanticCorpusFile = Join-Path $runDir "semantic-corpus.jsonl"
$semanticVectorFile = Join-Path $runDir "semantic-vectors.jsonl"
$semanticStandardFile = Join-Path $runDir "semantic-standard.json"

$files = Get-ChildItem -Path $scopePath -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\artifacts\\' -and $_.FullName -notmatch '\\.git\\' -and $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\venv\\' -and $_.FullName -notmatch '\\.env\\' -and $_.FullName -notmatch '\\env\\' -and $_.FullName -notmatch '\\node_modules\\' -and $_.FullName -notmatch '\\.venv-skill-seekers\\' } |
  ForEach-Object { ConvertTo-RepoRelativePath $_.FullName } |
  Sort-Object

Write-Utf8NoBom -Path $structureFile -Content (($files -join [Environment]::NewLine) + [Environment]::NewLine)

$extGroups = Get-ChildItem -Path $scopePath -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\artifacts\\' -and $_.FullName -notmatch '\\.git\\' -and $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\venv\\' -and $_.FullName -notmatch '\\.env\\' -and $_.FullName -notmatch '\\env\\' -and $_.FullName -notmatch '\\node_modules\\' -and $_.FullName -notmatch '\\.venv-skill-seekers\\' } |
  Group-Object {
    if ([string]::IsNullOrEmpty($_.Extension)) { "NO_EXT" }
    else { $_.Extension.TrimStart('.') }
  } |
  Sort-Object Name |
  ForEach-Object { "{0} {1}" -f $_.Name, $_.Count }

Write-Utf8NoBom -Path $statsFile -Content (($extGroups -join [Environment]::NewLine) + [Environment]::NewLine)

$pyLines = Get-ChildItem -Path $scopePath -Recurse -File -Include *.py -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\artifacts\\' -and $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\venv\\' -and $_.FullName -notmatch '\\.env\\' -and $_.FullName -notmatch '\\env\\' -and $_.FullName -notmatch '\\.venv-skill-seekers\\' } |
  Select-String -Pattern '^(from |import )' -SimpleMatch:$false -ErrorAction SilentlyContinue |
  ForEach-Object { "{0}:{1}:{2}" -f (ConvertTo-RepoRelativePath $_.Path), $_.LineNumber, $_.Line.Trim() }

$tsjsLines = Get-ChildItem -Path $scopePath -Recurse -File -Include *.ts,*.tsx,*.js,*.mjs,*.cjs -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\artifacts\\' -and $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\venv\\' -and $_.FullName -notmatch '\\.env\\' -and $_.FullName -notmatch '\\env\\' -and $_.FullName -notmatch '\\.venv-skill-seekers\\' } |
  Select-String -Pattern '^import |require\(' -SimpleMatch:$false -ErrorAction SilentlyContinue |
  ForEach-Object { "{0}:{1}:{2}" -f (ConvertTo-RepoRelativePath $_.Path), $_.LineNumber, $_.Line.Trim() }

Write-Utf8NoBom -Path $pyImportsFile -Content ((($pyLines | Sort-Object) -join [Environment]::NewLine) + [Environment]::NewLine)
Write-Utf8NoBom -Path $tsjsImportsFile -Content ((($tsjsLines | Sort-Object) -join [Environment]::NewLine) + [Environment]::NewLine)

Write-Utf8NoBom -Path $contextFile -Content @"
# Context Cards

- Module: <name>
- Responsibility: <one sentence>
- Inputs: <public API/params>
- Outputs: <result/side effects>
- Dependencies: <imports/calls>
- Dependents: <callers/importers>
- Risks: <coupling/global state>
- Evidence: <file:line or command>
"@

Write-Utf8NoBom -Path $impactFile -Content @"
# Impact Analysis

- Change Target: <path or symbol>
- Direct Impact: <direct callers/importers>
- Indirect Impact: <transitive consumers>
- High Risk Paths: <critical flows>
- Suggested Tests: <unit/integration/e2e>
- Rollback Plan: <feature flag/compat mode>
"@

$semanticCorpusLines = @()
$semanticVectorLines = @()

foreach ($path in $files) {
  $title = [System.IO.Path]::GetFileNameWithoutExtension($path)
  $ext = [System.IO.Path]::GetExtension($path).TrimStart('.')
  $parts = $path -split '/'
  $domain = if ($parts.Count -ge 2) { $parts[1] } else { 'root' }
  $semanticText = "path $path title $title domain $domain extension $ext"

  $tokens = Get-SemanticTokenList -Text $semanticText
  $tokenWeights = ConvertTo-TokenWeightMap -Tokens $tokens
  $vector = ConvertTo-HashedSparseVector -TokenWeightMap $tokenWeights -Dimensions 256
  $recordId = "cm_" + (Get-Sha1Hex -Text $path).Substring(0, 16)

  $corpusRecord = [ordered]@{
    schema_version = "1.0"
    id = $recordId
    type = "file"
    path = $path
    title = $title
    domain = $domain
    extension = $ext
    tokens = $tokens
    text = $semanticText
    source = "code-map"
  }

  $vectorRecord = [ordered]@{
    schema_version = "1.0"
    id = $recordId
    path = $path
    vector = $vector
  }

  $semanticCorpusLines += ($corpusRecord | ConvertTo-Json -Depth 8 -Compress)
  $semanticVectorLines += ($vectorRecord | ConvertTo-Json -Depth 8 -Compress)
}

Write-Utf8NoBom -Path $semanticCorpusFile -Content ((($semanticCorpusLines | Sort-Object) -join [Environment]::NewLine) + [Environment]::NewLine)
Write-Utf8NoBom -Path $semanticVectorFile -Content ((($semanticVectorLines | Sort-Object) -join [Environment]::NewLine) + [Environment]::NewLine)

$semanticStandard = [ordered]@{
  standard_version = "1.0"
  chunking = [ordered]@{
    unit = "file"
    scope = "src"
    text_template = "path + title + domain + extension"
  }
  vector = [ordered]@{
    algorithm = "hashing-tf"
    dimensions = 256
    normalization = "l2"
    metric = "cosine"
    tokenizer = "unicode-lower-split-nonalnum"
  }
  retrieval = [ordered]@{
    top_k_default = 10
    rerank = "none"
  }
}

Write-Utf8NoBom -Path $semanticStandardFile -Content (($semanticStandard | ConvertTo-Json -Depth 8) + [Environment]::NewLine)

$prevStructure = Join-Path $latestDir "structure-map.txt"
if (Test-Path $prevStructure) {
  $oldLines = [System.IO.File]::ReadAllLines($prevStructure)
  $newLines = [System.IO.File]::ReadAllLines($structureFile)

  $diff = Compare-Object -ReferenceObject $oldLines -DifferenceObject $newLines
  $added = $diff | Where-Object { $_.SideIndicator -eq '=>' } | Select-Object -ExpandProperty InputObject
  $removed = $diff | Where-Object { $_.SideIndicator -eq '<=' } | Select-Object -ExpandProperty InputObject

  $tracking = @()
  $tracking += "# Change Tracking"
  $tracking += ""
  $tracking += "- Scope: $effectiveScope"
  $tracking += "- Timestamp: $timestamp"
  $tracking += "- Added files: $($added.Count)"
  $tracking += "- Removed files: $($removed.Count)"
  $tracking += ""
  $tracking += "## Added (top 100)"
  $tracking += (($added | Select-Object -First 100) -join [Environment]::NewLine)
  $tracking += ""
  $tracking += "## Removed (top 100)"
  $tracking += (($removed | Select-Object -First 100) -join [Environment]::NewLine)

  Write-Utf8NoBom -Path $trackFile -Content (($tracking -join [Environment]::NewLine) + [Environment]::NewLine)
} else {
  Write-Utf8NoBom -Path $trackFile -Content @"
# Change Tracking

- Scope: $effectiveScope
- Timestamp: $timestamp
- Baseline run: no previous snapshot
"@
}

$manifestObj = [ordered]@{
  timestamp = $timestamp
  requested_scope = $Scope
  scope = $effectiveScope
  repo_root = $repoRoot
  commands = @(
    "update-codemap.ps1 -Scope $Scope",
    "structure scan",
    "imports scan",
    "semantic corpus build",
    "hashed vector build",
    "change tracking"
  )
  outputs = @(
    "structure-map.txt",
    "language-stats.txt",
    "imports-python.txt",
    "imports-tsjs.txt",
    "context-cards.md",
    "impact-analysis.md",
    "change-tracking.md",
    "semantic-corpus.jsonl",
    "semantic-vectors.jsonl",
    "semantic-standard.json",
    "manifest.json"
  )
}

$manifestJson = $manifestObj | ConvertTo-Json -Depth 5
Write-Utf8NoBom -Path $manifestFile -Content ($manifestJson + [Environment]::NewLine)

if (Test-Path $latestDir) {
  Remove-Item -Path $latestDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $latestDir | Out-Null
Copy-Item -Path (Join-Path $runDir "*") -Destination $latestDir -Recurse -Force

Write-Host "OK: code-map updated"
Write-Host "History: $runDir"
Write-Host "Latest : $latestDir"
