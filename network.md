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

### Grupa **disconnect**
W razie potrzeby zamknięcia połączenia server wyśle do klientów pakiet z grupy disconnect z pustą zawartością aby poinformować o tym fakcie klienta, tak samo klient może wysłać taki pakiet do servera aby ten go rozłączył.

### Grupa **account**
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
+ *nazwa_konta* to wysłana uprzednio nazwa konta do zalogowania.
+ *rezultat* to wartość Boolowska True albo False, gdzie True oznacza poprawne zalogowanie się, a False błąd w logowaniu.

W razie wystąpienia błędu w logowaniu pojawia się dodatkowe pole:
```python
"description":msg
```
+ *msg* to zdanie opisujące przyczynę nieudania się próby zalogowania, np. Błędne hasło, konto nie istnieje, jesteś już zalogowany.

#### Rejestracja
Rejestracja przebiega analogicznie do logowania, zmienia się tylko typ w danych pakietu.
```python
{
"type":"register",
"account": nazwa_konta,
"password": haslo
}
```
+ *nazwa_konta* to wybrany login składający się z dużych lub małych liter, dopuszczone również są myślniki.
+ *haslo* wybrane haslo do konta. **UWAGA!!!*** Wysyłane hasłą nie są w _ŻADEN_ sposób szyfrowane, miejcie to na uwadze zakładając własne konta!

Na tak spraperowany pakiet server odpowiada również rezultatem.

```python
{
"type":"result"
"action":"register"
"account": nazwa_konta
"result": rezultat
#"description": msg
}
```

+ *nazwa_konta* To wybrany login.
+ *rezultat* True - Rejestracja powiodła się, False - rejestracja zakończyła się niepowodzeniem, w takim wypadku pojawi się również pole "description".
+ *msg* Wiadomość informująca o przyczynie niepowodzenia, np. Login jest już zajęty.

## Grupa **game**
Pakiety z grupy game tyczą się świata gry.

### Wysłanie wiadomości chat
```python
{
"type":"chat",
"channel":kanal,
"message":wiadomosc
}
```
+ *kanal* Kanał czatu, na który wysyłamy wiadomość, obecnie istnieje tylko "global", jednak w przyszłości będzie więcej kanałów umożliwiających np rozmawianie z graczami w pobliżu.
+ *wiadomosc* Wiadomość do przesłania.

Na, który to dostaniemy my jak i reszta graczy odpowiedź:
```python
{
"type":"chat",
"channel":kanal,
"message":wiadomosc,
"player_id": id, # dla kanału global, local
}
```
+ *kanal* Kanał, na który gracz wysłał wiadomość.
Przewidziane kanały:
++ global kanał czatu, w którym wszyscy gracze otrzymują od siebie nawzajem wiadomości.
++ local kanał czatu obejmujący tylko aktualne pomieszczenie.
++ system wiadomośći systemowe.
++ game wiadomości związane z grą.
+ *wiadomosc* Treść wiadomości wysłanej przez gracza.
+ *id* Id gracza, który przesłał wiadomość (aby powiązać nick i id należy uprzednio odpytać server o listę graczy).

### Pobranie zawartości mapy (Do zaimplementowania)
Mapa w grze to dwuwymiarowa lista liczb, w tym momencie obsługiwane są tylko wartości.
+ 0 - w tym miejscu znajduje się podłoga.
+ 1 - w tym miejscu znajduje się ściana.

```python
{
"type":"map_request"
}
```
Na taki pakiet otrzymamy odpowiedź.
```python
{
"type":"map_content",
"width": szerokosc,
"height": wysokosc,
"reset": reset
"slice_x": sx,
"slice_y": sy,
"slice_width": sw,
"slice_height": sh,
"data": dane
"name": nazwa
}
```

Plansza jest przesyłana w kawałkach, tak aby nie przekroczyć maksymalnej wielkości pakietu wysyłanej na raz, więc aktualizujecie ją w kawałkach otrzymanych od servera.

+ *reset* True/False, czy klient powinien pozbyć się swojej wersji mapy, będzie ustawiane na true
w przypadku, kiedy przejdziemy do nowej lokacji i otrzymamy zupełnie nową planszę,
wraz z otrzymaniem fragmentu mapy z flagą reset należy przyjrzeć się nowej wielkości i szerokości planszy.
+ *slice_x* x'owa współrzędna otrzymanego prostokątnego wycinka planszy
+ *slice_y* y'owa współrzędna otrzymanego prostokątnego wycinka planszy
+ *slice_width* szerokość otrzymanego prostokątnego wycinka planszy
+ *slice_height* wysokość otrzymanego prostokątnego wycinka planszy
+ *dane* to lista liczb o długości szerokosc\*wysokosc, aby dostać się do poszczególnej komórki o współrzędnych (x,y) można posłużyć się prostym wzorem: komórka = dane[x+y*szerokosc].
+ *name* nazwa planszy, należy wyświetlać tylko tych graczy, którzy są na tej samej planszy, co my.

Server w przypadku zmian planszy samoczynnie wyśle nam nową wersje planszy.

### Pobranie listy graczy i ich postaci
Aby poprawnie wyświetlić planszę gry należy również przedstawić graczy i ich miejsce występowania, w tym celu należy odpytać server o aktualną listę graczy.

```python
{
"type":"player_list_request"
}
```

Otrzymamy odpowiedź

```python
{
"type":"player_list",
"players":lista_graczy
}
```

+ *lista_graczy* Pythonowa lista składająca się ze słowników, każdy "gracz" jest opisany w następujący sposób.

Listę graczy otrzymamy również w przypadku, kiedy ktoś podłączy się do servera i poprawnie zaloguje, nie ma potrzeby
okresowego odpytywania servera o listę graczy.

```python
player = {
  "x": x,
  "y': y,
  "name": imie
  "id": id
  "world": nazwa
}
```
+ *x* Pozycja x'owa gracza (kolumna, w której się znajduje).
+ *y* Pozycja y'owa gracza (wiersz, w którym się znajduje).
+ *name* Imię gracza, narazie jest to jego login.
+ *id* To unikalny numer identyfikujący gracza.
+ *world* Nazwa planszy, w ktorej gracz sie znajduje

### Poruszanie się postacią
```python
{
"type":"set_position",
"x":x,
"y":y
}
```
+ *x* Zadana pozycja x'owa gracza.
+ *y* Zadana pozycja y'owa gracza.

Po wysłaniu tego pakietu dostaniemy zaktualizowaną listę graczy, tak jak przy [pobieraniu listy graczy](###-Pobranie-listy-graczy-i-ich-postaci)

Odpowiedź na taki pakiet wygląda następująco:
```python
{
"type":"result",
"action":"set_position",
"x":x,
"y":y,
"result":rezultat
"description":opis
}
```

+ *rezultat* True/False, czy ruch się powiódł
+ *description* Pojawi się tylko jeśli ruch się nie powiedzie. Zawiera opis przyczyny niepowodzenia.

### Atakowanie innych postaci
Atakowanie innych postaci odbywa się poprzez wysłanie żądania zaatakowania konkretnego miejsca na planszy.
Jeśli podane miejsce zawiera postać i jest w zasięgu naszej broni, to atak się powiedzie.

```python
{
"type":"attack",
"x":x,
"y":y
}
```

Na co dostaniemy odpowiedź

```python
{
"type":"result",
"action":"attack",
"x":x,
"y":y,
"result":rezultat,
"description":opis,
}
```

+ *rezultalt* True/False, czy atak się powiódł
+ *description* Pojawi się tylko jeśli atak się nie powiedzie. Zawiera słowny opis przyczyny niepowodzenia.

### Odpytanie o własne statystyki
Aby dowiedzieć się, jakie statystyki posiada nasza postać należy wysłać pakiet
```python
{
"type":"stats_request",
}
```

Odpowiedź:

```python
{
"type":"stats",
"target":"player",
"player_id":id_gracza,
"strength": sila,
"dexterity": zrecznosc,
"wisdom": madrosc,
"health": punkty_zycia,
"health_capacity": maksymalne_punkty_zycia,
"mana": punkty_many,
"mana_capacity": maksymalne_punkty_many
}
```

+ *target* rodzaj obiektu, którego statystyki otrzymaliśmy, narazie zawsze będzie "player"
+ *player\_id* jeśli "target"="player", to to jest id gracza, którego statystyki są w pakiecie, będzie to nasze id
+ *strength* Siła
+ *dexterity* Zręczność
+ *wisdom* Mądrość
+ *health* Aktualne punkty życia
+ *health\_capacity*  Maksymalna ilość punktów życia, jaką obiekt w tym momencie może posiadać
+ *mana* Aktualne punkty many
+ *mana_capacity* Maksymalna ilość punktów many, jaką obiekt w tym momencie może posiadać

