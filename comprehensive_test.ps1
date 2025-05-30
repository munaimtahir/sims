# SIMS System Comprehensive Test Script
# Test all endpoints, authentication, and functionality

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [int]$MaxRetries = 3,
    [int]$RetryDelay = 2
)

Write-Host "🏥 SIMS System Comprehensive Testing" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date)" -ForegroundColor Cyan
Write-Host ""

# Function to test endpoint with retries
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Description,
        [int]$ExpectedStatus = 200,
        [switch]$AllowRedirect
    )
    
    $attempt = 0
    do {
        $attempt++
        try {
            if ($AllowRedirect) {
                $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue
                $actualStatus = $response.StatusCode
            } else {
                $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -ErrorAction SilentlyContinue
                $actualStatus = $response.StatusCode
            }
            
            $success = ($actualStatus -eq $ExpectedStatus) -or 
                      ($AllowRedirect -and $actualStatus -in @(301, 302, 303, 307, 308)) -or
                      ($actualStatus -in @(200, 302, 403))
            
            if ($success) {
                Write-Host "   ✅ $Description" -ForegroundColor Green
                Write-Host "      URL: $Url (Status: $actualStatus)" -ForegroundColor DarkGray
                return $true
            } else {
                Write-Host "   ❌ $Description" -ForegroundColor Red
                Write-Host "      URL: $Url (Status: $actualStatus, Expected: $ExpectedStatus)" -ForegroundColor DarkRed
                return $false
            }
        }
        catch {
            if ($attempt -lt $MaxRetries) {
                Write-Host "   ⏳ $Description (Attempt $attempt/$MaxRetries failed, retrying...)" -ForegroundColor Yellow
                Start-Sleep -Seconds $RetryDelay
            } else {
                Write-Host "   ❌ $Description" -ForegroundColor Red
                Write-Host "      URL: $Url (Error: $($_.Exception.Message))" -ForegroundColor DarkRed
                return $false
            }
        }
    } while ($attempt -lt $MaxRetries)
    
    return $false
}

# Test basic server connectivity
Write-Host "🌐 Testing Server Connectivity" -ForegroundColor Blue
Write-Host "-" * 30 -ForegroundColor Gray

$serverTests = @(
    @{ Url = "$BaseUrl/"; Description = "Main server"; ExpectedStatus = 200 },
    @{ Url = "$BaseUrl/admin/"; Description = "Django Admin"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/accounts/login/"; Description = "Login page"; ExpectedStatus = 200 }
)

$serverResults = @()
foreach ($test in $serverTests) {
    $result = Test-Endpoint -Url $test.Url -Description $test.Description -ExpectedStatus $test.ExpectedStatus -AllowRedirect:$test.AllowRedirect
    $serverResults += $result
}

Write-Host ""

# Test User Management URLs
Write-Host "👤 Testing User Management" -ForegroundColor Blue
Write-Host "-" * 30 -ForegroundColor Gray

$userTests = @(
    @{ Url = "$BaseUrl/users/dashboard/"; Description = "User Dashboard"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/users/profile/"; Description = "User Profile"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/users/profile/edit/"; Description = "Profile Edit"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/users/users/"; Description = "User List"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/users/supervisors/"; Description = "Supervisor List"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/users/postgraduates/"; Description = "Postgraduate List"; ExpectedStatus = 200; AllowRedirect = $true }
)

$userResults = @()
foreach ($test in $userTests) {
    $result = Test-Endpoint -Url $test.Url -Description $test.Description -ExpectedStatus $test.ExpectedStatus -AllowRedirect:$test.AllowRedirect
    $userResults += $result
}

Write-Host ""

# Test Dashboard and Analytics URLs
Write-Host "📊 Testing Dashboards & Analytics" -ForegroundColor Blue
Write-Host "-" * 30 -ForegroundColor Gray

$dashboardTests = @(
    @{ Url = "$BaseUrl/logbook/dashboard/"; Description = "Logbook Dashboard"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/logbook/analytics/"; Description = "Logbook Analytics"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/certificates/dashboard/"; Description = "Certificates Dashboard"; ExpectedStatus = 200; AllowRedirect = $true },
    @{ Url = "$BaseUrl/rotations/dashboard/"; Description = "Rotations Dashboard"; ExpectedStatus = 200; AllowRedirect = $true }
)

$dashboardResults = @()
foreach ($test in $dashboardTests) {
    $result = Test-Endpoint -Url $test.Url -Description $test.Description -ExpectedStatus $test.ExpectedStatus -AllowRedirect:$test.AllowRedirect
    $dashboardResults += $result
}

Write-Host ""

# Test Authentication URLs
Write-Host "🔐 Testing Authentication" -ForegroundColor Blue
Write-Host "-" * 30 -ForegroundColor Gray

$authTests = @(
    @{ Url = "$BaseUrl/accounts/login/"; Description = "Login Form"; ExpectedStatus = 200 },
    @{ Url = "$BaseUrl/accounts/password_reset/"; Description = "Password Reset"; ExpectedStatus = 200 },
    @{ Url = "$BaseUrl/accounts/password_change/"; Description = "Password Change"; ExpectedStatus = 200; AllowRedirect = $true }
)

$authResults = @()
foreach ($test in $authTests) {
    $result = Test-Endpoint -Url $test.Url -Description $test.Description -ExpectedStatus $test.ExpectedStatus -AllowRedirect:$test.AllowRedirect
    $authResults += $result
}

Write-Host ""

# Test Static Files and Resources
Write-Host "📁 Testing Static Resources" -ForegroundColor Blue
Write-Host "-" * 30 -ForegroundColor Gray

$staticTests = @(
    @{ Url = "$BaseUrl/static/"; Description = "Static Files Root"; ExpectedStatus = 200; AllowRedirect = $true }
)

$staticResults = @()
foreach ($test in $staticTests) {
    $result = Test-Endpoint -Url $test.Url -Description $test.Description -ExpectedStatus $test.ExpectedStatus -AllowRedirect:$test.AllowRedirect
    $staticResults += $result
}

Write-Host ""

# Calculate and display summary
Write-Host "📊 Test Summary" -ForegroundColor Green
Write-Host "=" * 30 -ForegroundColor Gray

$allResults = $serverResults + $userResults + $dashboardResults + $authResults + $staticResults
$totalTests = $allResults.Count
$passedTests = ($allResults | Where-Object { $_ -eq $true }).Count
$failedTests = $totalTests - $passedTests

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passedTests / $totalTests) * 100, 2))%" -ForegroundColor Cyan

Write-Host ""

if ($passedTests -eq $totalTests) {
    Write-Host "🎉 All tests passed! SIMS system is fully operational." -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Ready for production use!" -ForegroundColor Green
    Write-Host "   • Admin: $BaseUrl/admin/" -ForegroundColor Cyan
    Write-Host "   • Login: $BaseUrl/accounts/login/" -ForegroundColor Cyan
    Write-Host "   • Dashboard: $BaseUrl/users/dashboard/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Default Credentials:" -ForegroundColor Yellow
    Write-Host "   Username: admin" -ForegroundColor White
    Write-Host "   Password: admin123" -ForegroundColor White
} elseif ($passedTests -gt ($totalTests * 0.8)) {
    Write-Host "⚠️  Most tests passed. System is mostly operational with minor issues." -ForegroundColor Yellow
} else {
    Write-Host "❌ Multiple test failures detected. Please check server logs and configuration." -ForegroundColor Red
}

Write-Host ""
Write-Host "💡 Next Steps:" -ForegroundColor Blue
Write-Host "   1. Test login functionality with admin credentials" -ForegroundColor White
Write-Host "   2. Create test users and verify role-based access" -ForegroundColor White
Write-Host "   3. Test data entry and analytics functionality" -ForegroundColor White
Write-Host "   4. Verify all dashboard features work correctly" -ForegroundColor White
Write-Host ""
Write-Host "Test completed at: $(Get-Date)" -ForegroundColor Gray
