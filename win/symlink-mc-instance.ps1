$instance_dir = "D:\\MultiMC\\instances"
$nextcloud_dir = "E:\\nextcloud\\Minecraft\\"

Write-Host "Gathering data for symlink..."
$instance_name = Read-Host -Prompt "Instance name"
$client_mods_dir = Read-Host -Prompt "Client mods folder (empty to skip)"

# The first is located in MultiMC, second in nextcloud
# "config" = "nextcloud_config"
$symlinks = @{
  "config" = "config";
  "saves" = "saves";
  "schematics" = "schematics";
  "screenshots" = "screenshots";
}

if ($client_mods_dir.Length -ne 0) {
  $symlinks.Add("mods", "client-mods\\$client_mods_dir")
}

foreach ($h in $symlinks.GetEnumerator()) {
  $multimc_link = "$instance_dir\\$instance_name\\.minecraft\\" + $h.Name
  $nextcloud_target = $nextcloud_dir + $h.Value
  New-Item -ItemType SymbolicLink -Path "$multimc_link" -Target "$nextcloud_target"
}
