param(
  [Parameter(Mandatory = $true)][string]$Query,
  [int]$TopK = 10,
  [string]$CorpusPath = ""
)

$ErrorActionPreference = "Stop"

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

function Get-SemanticTokenList {
  param([Parameter(Mandatory = $true)][string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) {
    return @()
  }
  $normalized = $Text.ToLowerInvariant().Replace('\\', '/').Replace('_', ' ').Replace('-', ' ')
  return [System.Text.RegularExpressions.Regex]::Split($normalized, '[^\p{L}\p{Nd}]+') |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and $_.Length -ge 2 }
}

function ConvertTo-HashedSparseVector {
  param(
    [Parameter(Mandatory = $true)][hashtable]$TokenWeightMap,
    [int]$Dimensions = 256
  )

  $buckets = @{}
  foreach ($token in $TokenWeightMap.Keys) {
    $sha1 = [System.Security.Cryptography.SHA1]::Create()
    try {
      $bytes = [System.Text.Encoding]::UTF8.GetBytes($token)
      $hashBytes = $sha1.ComputeHash($bytes)
      $hashHex = ([BitConverter]::ToString($hashBytes)).Replace('-', '').ToLowerInvariant().Substring(0, 8)
      $idx = [Convert]::ToInt32($hashHex, 16) % $Dimensions
    }
    finally {
      $sha1.Dispose()
    }
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

function Get-SparseDotScore {
  param(
    [Parameter(Mandatory = $true)]$QueryVector,
    [Parameter(Mandatory = $true)]$DocVector
  )

  $queryMap = @{}
  for ($i = 0; $i -lt $QueryVector.indices.Count; $i++) {
    $queryMap[[int]$QueryVector.indices[$i]] = [double]$QueryVector.values[$i]
  }

  $score = 0.0
  for ($j = 0; $j -lt $DocVector.indices.Count; $j++) {
    $idx = [int]$DocVector.indices[$j]
    if ($queryMap.ContainsKey($idx)) {
      $score += $queryMap[$idx] * [double]$DocVector.values[$j]
    }
  }

  return [Math]::Round($score, 6)
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
if ([string]::IsNullOrWhiteSpace($CorpusPath)) {
  $CorpusPath = Join-Path $repoRoot "artifacts/code-map/latest/semantic-vectors.jsonl"
}

if (-not (Test-Path $CorpusPath)) {
  throw "semantic vector file not found: $CorpusPath"
}

$queryTokens = Get-SemanticTokenList -Text $Query
$queryWeights = ConvertTo-TokenWeightMap -Tokens $queryTokens
$queryVector = ConvertTo-HashedSparseVector -TokenWeightMap $queryWeights -Dimensions 256

$records = @()
Get-Content $CorpusPath | ForEach-Object {
  if (-not [string]::IsNullOrWhiteSpace($_)) {
    $records += ($_ | ConvertFrom-Json)
  }
}

if ($records.Count -eq 0) {
  Write-Host "No semantic records found. Run update-codemap first and ensure src/ has files."
  exit 0
}

$scored = $records | ForEach-Object {
  $score = Get-SparseDotScore -QueryVector $queryVector -DocVector $_.vector
  [PSCustomObject]@{
    score = $score
    id = $_.id
    path = $_.path
  }
} | Sort-Object score -Descending | Select-Object -First $TopK

if ($scored.Count -eq 0) {
  Write-Host "No semantic hits for query: $Query"
  exit 0
}

$scored | Format-Table -AutoSize
