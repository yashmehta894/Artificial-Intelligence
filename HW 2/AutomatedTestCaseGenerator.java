import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class TestCases {
	public static void main(String[] args) {
		
//		for(int i = 0; i < 10; i++) {
//			makeTestCases();
//			System.out.println();
//		}
		 for (int k = 0; k < dim; k++) {
	         for ( int j = 0; j <= k; j++ ) {
	         int i = k - j;
	         System.out.print( array[i][j] + " " );
	         }
	         System.out.println();
	         }
	}

	private static void makeTestCases() {
		Random rs = new Random();
		int beds = rs.nextInt(40);
		System.out.println(beds);
		int slots = rs.nextInt(40);
		System.out.println(slots);
		System.out.println(0);
		System.out.println(0);
		int numberOfApplicant = rs.nextInt(100);
		System.out.println(numberOfApplicant);
		List<String> result = makeApplicants(numberOfApplicant);
		for(String oneApplicant : result) {
			System.out.println(oneApplicant);
		}
	}

	private static List<String> makeApplicants(int numberOfApplicant) {
		Random rs = new Random();
		List<String> result = new ArrayList<>();
		for(int i = 0; i < numberOfApplicant; i++) {
			String applicant = "";
			if(i + 1 > 9) {
				applicant += "000";
			} else {
				applicant += "0000";
			}
			applicant += i + 1 +"";
			if(rs.nextInt() % 2 == 0) {
				applicant += "F";
			} else {
				applicant += "M";
			}
			applicant += "0";
			String age = rs.nextInt(100) + "";
			if(Integer.parseInt(age) <= 9) {
				applicant += "0";
			}
			applicant += age;
			for(int j = 0; j < 4; j++) {
				if(rs.nextInt() % 2 == 0) {
					applicant += "Y";
				} else {
					applicant += "N";
				}
			}
			for(int k = 0; k < 7; k++) {
				applicant += rs.nextInt(2) + "";
			}
			
			result.add(applicant);
		}
		return result;
	}
}
