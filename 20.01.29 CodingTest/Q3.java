import java.util.*;

public int solution3(int[] coins) {
    
    //0으로 시작하는 coin array({0, 1, 0, 1, ...})
        int[] altered0 = new int[coins.length];
        int count0 = 0;
    
    //1로 시작하는 coin array({1, 0, 1, 0, ...})
        int[] altered1 = new int[coins.length];
        int count1 = 0;
        
    
        for(int i = 0; i < coins.length; i++){
            switch(i%2){
                case 0:
                    altered0[i] = 0;
                    altered1[i] = 1;
                    break;
                case 1:
                    altered0[i] = 1;
                    altered1[i] = 0;
                    break;
            }
        }
        
    //coins와 altered0, altered1의 element를 각각 비교하여 뒤집을 coin 수 비교 -> 둘 중 최솟값을 return
        for(int j = 0; j < coins.length; j++){
            if(coins[j] != altered0[j])
                count0++;
            else if(coins[j] != altered1[j])
                count1++;
        }
        
        return Math.min(count0, count1);
    }
