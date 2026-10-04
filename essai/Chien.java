package essai;



public class Chien extends Animal implements Comparable, Cloneable {
    private String nom;
    private int age;

    public Chien(String nom) {
        this.nom = nom;
    }

    public String aboyer(int fois) {
        return "Wouf";
    }
    public int compareTo(Object autre) {
    return 0;
    }
}