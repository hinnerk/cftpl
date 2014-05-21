"""
Uploader Module

The idea behind this was that we'd upload chef or salt config files to S3 and later use them to configure systems.

This has proven to be too slow and cumbersome, so we've removed this functionality.
"""

from boto.s3.key import Key
import os.path
import sys
import tarfile



def make_stack(config, name, role, indent=False):
    """
    creates and uploads configuration.

    Each upload produces a distinct url, valid for 30 days,
    which is subsequently included into the template variables
    to be used in later steps. As such the order of execution
    here is important as a later step may use the variable set
    by an earlier one.
    """
    for c in config.get('data'):
        inst = TYPE_MAPPING.get(c['type'])(config, name, c['template'], c['file_name'], c['url'])
        url = inst.upload()
        if "url" in c:
            config[c["url"]] = url
    return make_cloudformation_config(config, name, role, indent)


class FileUpload(object):
    def __init__(self, config, name, template, file_name, url):
        self.config = config
        self.name = name
        self.template = template
        self.file_name = file_name
        self.url = url
        self.bucket = self.config.get(CONSTANTS.DEVOPS_BUCKET)
        self.path = os.path.abspath(os.path.join(self.config[CONSTANTS.WORK_DIR], self.template))
        user = self.config.get(CONSTANTS.ACCOUNT)
        password = get_key(name, user)
        s3_con = boto.connect_s3(user, password)
        self.con = s3_con.get_bucket(self.bucket)

    def upload(self):
        print("Uploading {} to {}".format(self.key, self.bucket))
        k = Key(self.con)
        k.key = self.key
        k.set_contents_from_string(self.value)
        return k.generate_url(expires_in=600, force_http=True)  # 10 minutes

    @property
    def key(self):
        return self.file_name

    @property
    def value(self):
        if not os.path.isfile(self.path):
            print('ERROR: Path "{}" does not exist!'.format(self.path))
            sys.exit(24)
        template = open(self.path).read()
        return format_template(template, self.config)


class DirUpload(FileUpload):
    @property
    def value(self):
        dir_name = self.template.split(os.path.sep)[-1]

        def filter_path(tarinfo):
            """
            Change path of added files and reset owner.
            """
            if not dir_name in tarinfo.name:
                return None
            file_name = tarinfo.name.split(os.path.sep)
            file_name = file_name[file_name.index(dir_name):]
            tarinfo.name = os.path.sep.join(['.'] + file_name)
            tarinfo.uid = tarinfo.gid = 0
            tarinfo.uname = tarinfo.gname = "root"
            return tarinfo

        f = FakeFile()
        tar_file = tarfile.open(name=self.file_name, mode='w|gz', fileobj=f)
        tar_file.add(self.path, filter=filter_path)
        tar_file.close()
        return f.data


TYPE_MAPPING = {
    'file': FileUpload,
    'dir': DirUpload
}


class FakeFile(object):
    new = True

    def __init__(self):
        self.data = ""
        self.pos = 0

    def write(self, block):
        self.new = False
        self.pos += len(block)
        self.data += block

    def close(self):
        pass

    def tell(self):
        return self.pos


    def seek(self, pos):
        if pos == 0 and self.new:
            return True
        raise Exception("FakeFiles can't seek!")