# Program flowchart

```mermaid
flowchart TD
    A([Start]) --> B[Login screen<br/>First time? Create new account]
    B -- Log in --> C[/Enter master password/] --> D[Derive key and decrypt]
    B -- First time? Create account --> E[/Create account and choose master password/] --> F[Create new vault]
    D --> G{Decryption OK?}
    G -- No --> I[Show error] --> Z([Exit])
    G -- Yes --> H{Menu}
    F --> H
    H -- Add --> J[Store site, username, password] --> K[Encrypt and save]
    H -- Get --> L[Show entry] --> H
    H -- Delete --> M[Remove entry] --> K
    H -- List --> N[Show sites] --> H
    H -- New password --> O[Generate random password] --> H
    K --> H
    H -- Quit --> Z
```
