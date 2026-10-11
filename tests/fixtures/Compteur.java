package tests.fixtures;

import java.util.ArrayList;
import java.util.List;

public class Compteur {
    private static int total;
    public static final String NOM = "compteur";
    List<Chien> chiens = new ArrayList<>();

    void ajouter(Chien chien) {
        chiens.add(chien);
        total++;
    }

    public Animal premier() {
        return new Animal();
    }
}
