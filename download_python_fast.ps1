# Fast Python Embedded Download Tool
param(
    [string]$OutputPath = ".\dist\cache\python-3.10.11-embed-amd64.zip"
)

$ErrorActionPreference = "Stop"

# Create cache directory
$cacheDir = Split-Path $OutputPath
if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
}

# Mirror list (sorted by speed)
$mirrors = @(
    @{
        Name = "npmmirror"
        Url = "https://registry.npmmirror.com/-/binary/python/3.10.11/python-3.10.11-embed-amd64.zip"
    },
    @{
        Name = "Huawei Cloud"
        Url = "https://mirrors.huaweicloud.com/python/3.10.11/python-3.10.11-embed-amd64.zip"  
    },
    @{
        Name = "Aliyun"
        Url = "https://mirrors.aliyun.com/python-release/windows/python-3.10.11-embed-amd64.zip"
    },
    @{
        Name = "Python Official"
        Url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
    }
)

$expectedSize = 8 * 1024 * 1024  # At least 8MB

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Python Embedded Fast Download Tool" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

foreach ($mirror in $mirrors) {
    Write-Host "Trying $($mirror.Name)..." -ForegroundColor Yellow
    Write-Host "  URL: $($mirror.Url)" -ForegroundColor Gray
    
    try {
        $tempFile = "$OutputPath.tmp"
        
        # Use BITS (Background Intelligent Transfer Service)
        Write-Host "`nUsing BITS transfer service..." -ForegroundColor Green
        
        $job = Start-BitsTransfer -Source $mirror.Url -Destination $tempFile -Asynchronous -DisplayName "Python Embedded Download"
        
        # Show progress
        $lastProgress = -1
        $startTime = Get-Date
        while ($job.JobState -eq "Transferring" -or $job.JobState -eq "Connecting") {
            $progress = 0
            if ($job.BytesTotal -gt 0) {
                $progress = [math]::Round(($job.BytesTransferred / $job.BytesTotal) * 100, 1)
            }
            
            if ($progress -ne $lastProgress) {
                $mb = [math]::Round($job.BytesTransferred / 1MB, 2)
                $totalMb = [math]::Round($job.BytesTotal / 1MB, 2)
                $elapsed = ((Get-Date) - $startTime).TotalSeconds
                $speed = if ($elapsed -gt 0) { [math]::Round($job.BytesTransferred / $elapsed / 1KB, 0) } else { 0 }
                
                Write-Host ("`r  Progress: {0}% ({1} MB / {2} MB) - Speed: {3} KB/s" -f $progress, $mb, $totalMb, $speed) -NoNewline -ForegroundColor Cyan
                $lastProgress = $progress
            }
            
            Start-Sleep -Milliseconds 200
            
            # Timeout after 60 seconds
            if (((Get-Date) - $startTime).TotalSeconds -gt 60) {
                Write-Host "`n  Timeout! Trying next mirror..." -ForegroundColor Red
                Remove-BitsTransfer -BitsJob $job -ErrorAction SilentlyContinue
                break
            }
        }
        
        Write-Host ""  # New line
        
        if ($job.JobState -eq "Transferred") {
            Complete-BitsTransfer -BitsJob $job
            
            # Verify file
            if (Test-Path $tempFile) {
                $fileSize = (Get-Item $tempFile).Length
                if ($fileSize -gt $expectedSize) {
                    # Move to final location
                    Move-Item -Path $tempFile -Destination $OutputPath -Force
                    
                    Write-Host "`nSUCCESS! Download completed!" -ForegroundColor Green
                    Write-Host "  File size: $([math]::Round($fileSize / 1MB, 2)) MB" -ForegroundColor Green
                    Write-Host "  Saved to: $OutputPath`n" -ForegroundColor Green
                    exit 0
                } else {
                    Write-Host "  File size invalid ($([math]::Round($fileSize / 1MB, 2)) MB), trying next mirror..." -ForegroundColor Red
                    Remove-Item $tempFile -ErrorAction SilentlyContinue
                }
            }
        } elseif ($job) {
            Write-Host "  Transfer failed: $($job.JobState)" -ForegroundColor Red
            Remove-BitsTransfer -BitsJob $job -ErrorAction SilentlyContinue
        }
        
    } catch {
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Cleanup
        if ($job) {
            Remove-BitsTransfer -BitsJob $job -ErrorAction SilentlyContinue
        }
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Red
Write-Host " All mirrors failed" -ForegroundColor Red
Write-Host "========================================`n" -ForegroundColor Red

exit 1
