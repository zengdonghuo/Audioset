	The description of how to get the audio event segement?

	This file is about how to use three files (eval_segments.csv, balanced_train_segments.csv, class_labels_indices.csv) which come from google audioset location {https://research.google.com/audioset///download.html}.
	For instance, if you want to get all audio of subcategories of 'Singing', the related python file is main.py.
	1.  You should load those three files:
	lid_lname_dict,lname_lid_dict, vid_lid_dict, vid_startend_dict = AudiosetStart()
	lid_lname_dict and lname_lid_dict are two dictionary of label id and label name exchange. vid_lid_dict is a dictionary of video id (YouTube id) and label id. vid_startend_dictis a dictionary of video id and start time, end time.
	2. You can define and get your excepted labels.
	   1> use list type data structure to define your labels.
	   2> then get all your excepted labels, adding all other labels with a list input to getOffspring function, the adding to the defined label list.
	3. get all audio items which their labels are in your excepted labels list.
	4. divided all audio items with the number of labels which appear in your first defined label list into only one label, two labels and more than 2 labels.
	5. Suppose you want to get all audio set which is only one label appear in your first defined label list. You know, I have all audioset with 100% assessment, but maybe they still can't coverge all your expected labels, so you have to get by yourself. You can do like this:
	  1> you can use get_video() function to download all full video on your own hard disk. Two args: video id list and the path of hard disk.
	  2> Once you get full video, you can use getSegment() function with inputs:
 	   a) updated dictionary of video id and start time, end time;
	   b) full video path
	   c) video segment path
	  3> then use moving() function to copy out your expect video segment.
	Otherwise, if all label are 100% assessment, you can ignore step 1> and 2>.
	6. After the previous steps, you can use getaudios() function with inputs:
	   1> Your video segment storage path
	   2> Your own audio segment path
