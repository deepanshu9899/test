#!/bin/bash
check_remove_pwc_certificates() {
    # Specify the path to the keychain
    keychain_path="/Users/ltuser/Library/Keychains/login.keychain-db"

    # Dump the keychain and filter certificates with "PwC" in their common name
    cert_info=$(sudo security dump-keychain "$keychain_path" | grep -E 'alis.*PwC')

    # Extract and delete the certificates by common name
    while IFS= read -r line; do
        common_name=$(echo "$line" | sed 's/.*"alis"<blob>=//; s/\\x20//g; s/\"//g')
        echo "Attempting to delete certificate with common name: \"$common_name\""
        sudo security delete-certificate -c "$common_name" "$keychain_path"
        echo "Deleted certificate with common name: \"$common_name\""
    done <<< "$cert_info"
}
check_remove_pwc_certificates
