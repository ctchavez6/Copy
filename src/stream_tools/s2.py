import cv2
from experiment_set_up import find_previous_run as fpr
import os
import numpy as np
from image_processing import bit_depth_conversion as bdc
from coregistration import img_characterization as ic


def step_two(stream, continue_stream):
    y_n_msg = "Proceed? (y/n): "

    """
    Gameplan:
        1st: If user chooses to go through step 2's coreg process, then great, use that warp
        2nd: If user chooses NOT to coreg, Load in from last run
                THIS WILL REQUIRE SAVING
    """

    previous_run_directory = fpr.get_latest_run_direc(path_override=True, path_to_exclude=stream.current_run)
    prev_wp1_path = os.path.join(previous_run_directory, "wm1.npy")
    prev_wp1_exist = os.path.exists(prev_wp1_path)
    coregister_ = "n"

    if prev_wp1_exist:
        use_last_wp1 = input("Step 2 - You created a Warp Matrix 1 last run. Would you like to use it? (y/n)  ")
        if use_last_wp1.lower() == "y":
            stream.warp_matrix = np.load(prev_wp1_path)
        else:
            coregister_ = "y"
    else:
        coregister_ = input("Step 2 - New Co-Registration with with Euclidean Transform? -  {}".format(y_n_msg))

    """
    coregister_ = input("Step 2 - Co-Registration: "
                        "\n\tUse Warp Matrix Run from Previous run? (y)"
                        "\n\tElse, brand new Co-Registration? (n)")
    """

    if coregister_.lower() == "y":
        continue_stream = True
        a_8bit = bdc.to_8_bit(stream.current_frame_a)
        b_8bit = bdc.to_8_bit(stream.current_frame_b)
        warp_ = ic.get_euclidean_transform_matrix(a_8bit, b_8bit)

        # np.save('wp1.npy', warp_)

        stream.warp_matrix = warp_

        a, b, tx = warp_[0][0], warp_[0][1], warp_[0][2]
        c, d, ty = warp_[1][0], warp_[1][1], warp_[1][2]

        print("\tTranslation X:{}".format(tx))
        print("\tTranslation Y:{}\n".format(ty))

        scale_x = np.sign(a) * (np.sqrt(a ** 2 + b ** 2))
        scale_y = np.sign(d) * (np.sqrt(c ** 2 + d ** 2))

        print("\tScale X:{}".format(scale_x))
        print("\tScale Y:{}\n".format(scale_y))

        phi = np.arctan2(-1.0 * b, a)
        print("\tPhi Y (rad):{}".format(phi))
        print("\tPhi Y (deg):{}\n".format(np.degrees(phi)))

        temp_a_8bit = np.array(stream.current_frame_a, dtype='uint8')  # bdc.to_8_bit()
        temp_b_prime_8bit = np.array(stream.current_frame_b, dtype='uint8')
        # temp_b_prime_8bit = bdc.to_8_bit(stream.current_frame_b)
        GOOD_MATCH_PERCENT = 0.10
        orb = cv2.ORB_create(nfeatures=10000, scoreType=cv2.ORB_FAST_SCORE, nlevels=20)
        keypoints1, descriptors1 = orb.detectAndCompute(temp_a_8bit, None)
        keypoints2, descriptors2 = orb.detectAndCompute(temp_b_prime_8bit, None)

        print("A has {} key points".format(len(keypoints1)))
        print("B has {} key points".format(len(keypoints2)))
        # cv2.drawMatchesKnn expects list of lists as matches.

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)
        matches.sort(key=lambda x: x.distance, reverse=False)

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        knn_matches = bf.knnMatch(descriptors1, descriptors2, k=2)
        lowe_ratio = 0.89

        # Apply ratio test_RminRmax
        good_knn = []

        for m, n in knn_matches:
            if m.distance < lowe_ratio * n.distance:
                good_knn.append([m])

        print("Percentage of Matches within Lowe Ratio of 0.89: {0:.4f}".format(
            100 * float(len(good_knn)) / float(len(knn_matches))))

        imMatches = cv2.drawMatches(temp_a_8bit, keypoints1, temp_b_prime_8bit, keypoints2, matches[:25], None)
        cv2.imshow("DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING",
                   cv2.resize(imMatches, (int(imMatches.shape[1] * 0.5), int(imMatches.shape[0] * 0.5))))
        cv2.waitKey(60000)
        cv2.destroyAllWindows()

    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
        a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
        b_as_16bit = bdc.to_16_bit(stream.current_frame_b)
        cv2.imshow("A", a_as_16bit)
        cv2.imshow("B Prime", b_as_16bit)
        continue_stream = stream.keep_streaming()

    cv2.destroyAllWindows()