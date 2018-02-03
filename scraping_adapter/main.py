import os
import sys
import json
import shutil
import urllib
from processor.wordai_rewriter_processor import WordAIProcessor


class ScrapingAdapter:

    contents_subdir_name= 'files'
    metadata_filename = "metadata.json"

    def __init__(self, source_dir, target_dir, source_posts_dir_name='articles', sequence_prefix="posts", filename_field='article',
                 content_processor=WordAIProcessor()):
        self.target_dir = target_dir
        self.posts_dir_path = os.path.join(source_dir, source_posts_dir_name)
        self.posts_metadata_file_path = os.path.join(source_dir, "{}.info".format(source_posts_dir_name))
        if not os.path.isdir(source_dir) \
            or not os.path.isdir(self.posts_dir_path) \
            or not os.path.isfile(self.posts_metadata_file_path):
                print "Source Directory '{0}' should have posts directory '{1}' and metadata file '{1}.info'"\
                    .format(source_dir, source_posts_dir_name)
                sys.exit(1)
        with open(self.posts_metadata_file_path, 'r') as f:
            self.source_metadata = json.loads(f.read())
        self.sequence_prefix = sequence_prefix
        self.filename_field = filename_field
        self.content_processor = content_processor

    def generate(self):
        idx = 0
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)
        for post_metadata in self.source_metadata:
            idx = idx + 1
            post_name = post_metadata[self.filename_field]
            source_post_file_path = os.path.join(self.posts_dir_path, post_name)
            print "Processing post: {}".format(source_post_file_path)
            if not self.validate(idx, post_name, source_post_file_path):
                continue
            target_dir_path = self.get_target_dir_path(idx)
            os.mkdir(target_dir_path)
            target_metadata = ScrapingAdapter.initialize_target_metadata(post_metadata, post_name)
            target_content_subdir_path = os.path.join(target_dir_path, self.contents_subdir_name)
            os.mkdir(target_content_subdir_path)
            self.process_post_content(post_name, source_post_file_path, target_content_subdir_path, target_metadata)
            self.copy_image_content(post_metadata, post_name, target_content_subdir_path, target_metadata)
            self.dump_metadata_json(target_dir_path, target_metadata)
            print "Generation for post '{0}' completed at index {1}.".format(post_name, idx)

    @staticmethod
    def initialize_target_metadata(post_metadata, post_name):
        target_metadata = {
            "article": post_name,
            "information": {
                "slug": post_metadata["information"]["slug"],
                "title": post_metadata["information"]["title"]
            }
        }
        return target_metadata

    def validate(self, idx, post_name, source_post_file_path):
        is_valid = True
        if not os.path.isfile(source_post_file_path):
            print "Error !! File {0} corresponding to post {1} not found. Skipping." \
                .format(source_post_file_path, post_name)
            is_valid = False
        target_dir_path = self.get_target_dir_path(idx)
        if os.path.isdir(target_dir_path):
            print "Target dir '{0}' for post '{1}' already exists. Skipping" \
                .format(target_dir_path, post_name)
            is_valid = False
        return is_valid

    def get_target_dir_path(self, idx):
        return os.path.join(self.target_dir, "%s%04d" % (self.sequence_prefix, idx))

    def dump_metadata_json(self, target_dir_path, target_metadata):
        with open(os.path.join(target_dir_path, self.metadata_filename), 'wb') as f:
            f.write(json.dumps(target_metadata))

    def copy_image_content(self, post_metadata, post_name, target_content_subdir_path, target_metadata):
        if 'title-img' in post_metadata['information'] and post_metadata["information"]["title-img"]:
            media_file_base_name = post_metadata["information"]["title-img"].split('/')[-1]
            target_media_file_path = os.path.join(target_content_subdir_path, media_file_base_name)
            if post_metadata["information"]["title-img"].startswith("http://") or \
                    post_metadata["information"]["title-img"].startswith("https://"):
                urllib.urlretrieve(post_metadata["information"]["title-img"], target_media_file_path)
                print "Downloaded '{0}' at '{1}'".format(post_metadata["information"]["title-img"],
                                                         target_media_file_path)
            else:
                shutil.copy(post_metadata["information"]["title-img"], target_media_file_path)
            target_metadata["information"]["title-img"] = os.path.join(self.contents_subdir_name, media_file_base_name)
        else:
            print "No title image data found for '{0}'".format(post_name)

    def process_post_content(self, post_name, source_post_file_path, target_content_subdir_path, target_metadata):
        target_content_file_path = os.path.join(target_content_subdir_path, post_name)
        with open(source_post_file_path) as f:
            processed_content = self.content_processor.process(f.read())
        with open(target_content_file_path, 'w') as f:
            f.write(processed_content)
        target_metadata["information"]["content-file"] = os.path.join(self.contents_subdir_name, post_name)

if __name__ == "__main__":
    adapter = ScrapingAdapter('/Users/dbansal/Work/MyCode/scraping/mic/Output',
                              '/Users/dbansal/Work/MyCode/wp-auto-poster/posts')
    adapter.generate()






