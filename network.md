# Opis protokołu internetowego
## Klasa Packet
Zawiera niezbędne metody do tworzenia pojedynczej jednostki komunikacji w architekturze naszej gry w relacji server <-> client.
Pakiet składa się z jego grupy i reszty zawartości oraz zawiera metody tworzenia pakietów z surowych danych binarnych i zamieniania ich na nie.

Założeniem jest wysyłanie wiadomości między klientem a serverem nie za pomocą metody socket.send a wykorzystywaniem pakiet.send(socket), która to automatycznie przeprowadza zamianę na dane binarne.

## Grupy pakietów
W tej chwili występują 2 grupy pakietów
1. **disconnect**
2. **account**
3. **game**

### disconnect
W razie potrzeby zamknięcia połączenia server wyśle do klientów pakiet z grupy disconnect z pustą zawartością aby poinformować o tym fakcie klienta, tak samo klient może wysłać taki pakiet do servera aby ten go rozłączył.

### account
Wszystkie pakiety z tej grupy tyczą się logowania do konta oraz rejestrowania nowego, można za ich pomocą obsłużyć następujące sytuacje, tworząc pakiet z grupy **account** i odpowiednio tworząc jego pole "data", które powinno być słownikiem:

#### Logowanie:
Należy przygotować słownik o następujących polach:
```python
{
"type":"login",
"account": nazwa_konta,
"password": haslo
}
```

+ *nazwa_konta* to login, który powinien być napisem składający się wyłącznie z dużych jak i małych liter, cyfr oraz myślnika
+ *haslo* to hasło, które powinno odpowiadać nadanemu. **UWAGA!!!*** Wysyłane hasłą nie są w _ŻADEN_ sposób szyfrowane, miejcie to na uwadze zakładając własne konta!

Server na takie zapytanie odpowiada pakietem oczywiście z grupy **account** składającym się z:
```python
{
"type":"result",
"action":"login",
"account": nazwa_konta,
"result": rezultat
#"description":msg - opcjonalne
}
```
+ *nazwa_konta* to wysłana uprzednio nazwa konta do zalogowania
+ *rezultat* to wartość Boolowska True albo False, gdzie True oznacza poprawne zalogowanie się, a False błąd w logowaniu.

W razie wystąpienia błędu w logowaniu pojawia się dodatkowe pole:
```python
"description":msg
```
+ *msg* to zdanie opisujące przyczynę nieudania się próby zalogowania, np. Błędne hasło, konto nie istnieje, jesteś już zalogowany

#### Rejestracja
Rejestracja przebiega analogicznie do logowania, zmienia się tylko typ w danych pakietu.
```python
{
"type":"register",
"account": nazwa_konta,
"password": haslo
}

+ *nazwa_konta* to wybrany login składający się z dużych lub małych liter, dopuszczone również są myślniki
+ *haslo* wybrane haslo do konta. **UWAGA!!!*** Wysyłane hasłą nie są w _ŻADEN_ sposób szyfrowane, miejcie to na uwadze zakładając własne konta!

Na tak spraperowany pakiet server odpowiada również rezultatem

```python
{
"type":"result"
"action":"register"
"account": nazwa_konta
"result": rezultat
#"description": msg
}

+ *nazwa_konta* To wybrany login
+ *rezultat* True - Rejestracja powiodła się, False - rejestracja zakończyła się niepowodzeniem, w takim wypadku pojawi się również pole "description"
+ *msg* Wiadomość informująca o przyczynie niepowodzenia, np. Login jest już zajęty.
