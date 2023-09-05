# Mango Scripts index

Script and signaturs for Mango Dev Env scripts.
The index is outputted as `resources.yml`

## To Build the repository and the signatures

Add which GPG key you want to use in `settings.yml`

Run build.py

```bash
python3 build.py
```

## To Build for local filesystem

Change settings and add the ABSOLUTE location of the `scripts` and `signatures`

## To generate your own index

- generate you own gpg key `gpg --gen-key`
- change which key you want to use in `key_name` field in `settings.yml`
- run the build command: `python3 build.py`

## Manage Dependencies

- export all the dependencies to `requirements.txt` use <b>pipreqs</b> `pip install pipreqs`
```bash
pip3 install pipreqs
pipreqs .
```
- install dependencies
```bash
pip3 install -r requirements.txt 
```