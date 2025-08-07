public class ModelData {
    private int Movement;
    private int Toughness;
    private int Saves;
    private int Wounds;
    private int Leadership;
    private int ObjectiveControl;
    private int InvulnSaves;

    // ModelData.java
    @Override
    public String toString() {
        return String.format(
            "Movement: %d\n" +
            "Toughness: %d\n" +
            "Save (SV): %d\n" +
            "Wounds: %d\n" +
            "Leadership (Ld): %d\n" +
            "Objective Control (OC): %d\n" +
            "Invulnerable Save: %d",
            Movement, Toughness, Saves, Wounds, Leadership, ObjectiveControl, InvulnSaves
        );
    }

    public ModelData(int Mv, int Tough, int Sv, int W, int Ld, int OC, int invulSv) {
        this.Movement           = Mv;
        this.Toughness          = Tough;
        this.Saves              = Sv;
        this.Wounds             = W;
        this.Leadership         = Ld;
        this.ObjectiveControl   = OC;
        this.InvulnSaves        = invulSv;
    }

    
    public int getMovement() {
        return Movement;
    }

    public int getToughness() {
        return Toughness;
    }

    public int getSaves() {
        return Saves;
    }

    public int getWounds() {
        return Wounds;
    }

    public int getLeadership() {
        return Leadership;
    }

    public int getObjectiveControl() {
        return ObjectiveControl;
    }

    public int getInvulnSaves() {
        return InvulnSaves;
    }
}
