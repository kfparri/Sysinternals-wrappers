./sigcheck.exe -t * -c | Export-csv -path result.csv

$item1 = Get-Content ref.csv
$item2 = Get-Content result.csv

$results = Compare-Object $item1 $item2

if ($test -eq $null)
{
    #Do something!
}