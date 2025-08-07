public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Dodekatheon2!");

        WeapData boltRifle = new WeapData("24", "2", "3+", 4, -1, "1");
        WeapData astartesChainsword = new WeapData("Melee", "5", "3+", 4, -1, "1");

        UnitData ud = new UnitData();
        ud.getWeapData(boltRifle);
        System.out.println();
        ud.getWeapData(astartesChainsword);
    }
}
